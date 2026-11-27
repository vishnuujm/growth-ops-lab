import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { createHandler } from "../supabase/functions/score-lead/handler.ts";

const icp = JSON.parse(readFileSync(new URL("../supabase/functions/score-lead/icp.json", import.meta.url), "utf8"));
const ENV = { INTAKE_SECRET: "s3cret", GEMINI_API_KEY: "k", GEMINI_MODEL: "m", SUPABASE_URL: "https://db.test", SUPABASE_SERVICE_ROLE_KEY: "sb_secret_x", DEMO_MODE: "true" };
const GOOD = { email: "Priya@Northwind.example", company_size: "51-200", role: "Head of Operations", timeline: "now", use_case: "automate reporting", first_name: "Priya", company: "Northwind" };
const aiSays = (answer) => () => Response.json({ candidates: [{ content: { parts: [{ text: typeof answer === "string" ? answer : JSON.stringify(answer) }] } }] });

function setup({ ai = aiSays({ score: 85, tier: "A", reason: "Good fit" }), env = {}, rows = [], dbDown = false, conflictOnce = false } = {}) {
  const calls = { ai: [], logs: [], leads: rows, headers: [] };
  let conflict = conflictOnce;
  const fakeFetch = async (url, init = {}) => {
    const body = init.body ? JSON.parse(init.body) : undefined;
    if (url.includes("generativelanguage")) { calls.ai.push(body); return ai(init); }
    calls.headers.push(init.headers);
    if (url.includes("events_log")) { calls.logs.push(body); return Response.json([body]); }
    if (dbDown) return new Response("{}", { status: 503 });
    if (init.method === "GET") return Response.json(calls.leads.slice(0, 1));
    if (init.method === "POST") {
      if (conflict) { conflict = false; calls.leads.push({ id: "other", email: body.email }); return new Response("{}", { status: 409 }); }
      const row = { id: "new-id", ...body }; calls.leads.push(row); return Response.json([row]);
    }
    Object.assign(calls.leads[0], body);
    return Response.json([calls.leads[0]]);
  };
  const all = { ...ENV, ...env };
  const handler = createHandler({ env: (k) => all[k], fetch: fakeFetch, icp, aiTimeoutMs: 20 });
  const send = async (payload, { secret = "s3cret", type = "application/json", method = "POST" } = {}) => {
    const body = method === "GET" ? undefined : typeof payload === "string" ? payload : type.includes("json") ? JSON.stringify(payload) : new URLSearchParams(payload).toString();
    const headers = { "content-type": type, ...(secret === null ? {} : { "x-intake-secret": secret }) };
    const res = await handler(new Request("https://fn.test", { method, headers, body }));
    return { status: res.status, json: await res.json() };
  };
  return { send, calls };
}

test("wrong or missing secret is refused and nothing is touched", async () => {
  const { send, calls } = setup();
  for (const secret of ["nope", "", null, "s3cret "+"x"]) assert.equal((await send(GOOD, { secret })).status, 401);
  assert.equal(calls.ai.length + calls.logs.length + calls.leads.length, 0);
  assert.equal((await setup({ env: { INTAKE_SECRET: "" } }).send(GOOD, { secret: "" })).status, 401);
});

test("only POST is accepted", async () => {
  assert.equal((await setup().send(GOOD, { method: "GET" })).status, 405);
});

test("good enquiry: AI score saved, email lowercased, marked demo", async () => {
  const { send, calls } = setup();
  const { status, json } = await send(GOOD);
  assert.equal(status, 200);
  assert.deepEqual(json, { lead_id: "new-id", email: "priya@northwind.example", score: 85, tier: "A", reason: "Good fit", scored_by: "gemini", is_duplicate: false });
  assert.equal(calls.leads[0].is_demo, true);
  assert.equal(calls.leads[0].source, "webflow_form");
  assert.equal(calls.headers[0].authorization, undefined);
});

test("form-encoded posts are accepted", async () => {
  const { status } = await setup().send(GOOD, { type: "application/x-www-form-urlencoded" });
  assert.equal(status, 200);
});

test("no name, email address or company is sent to the AI", async () => {
  const { send, calls } = setup();
  await send(GOOD);
  const sent = JSON.stringify(calls.ai[0]).toLowerCase();
  for (const secretish of ["priya", "northwind"]) assert.ok(!sent.includes(secretish), secretish);
});

test("grade follows the score even if the AI contradicts itself", async () => {
  const { json } = await setup({ ai: aiSays({ score: 20, tier: "A", reason: "x" }) }).send(GOOD);
  assert.equal(json.tier, "C");
});

for (const [name, options] of Object.entries({
  "limit reached": { ai: () => new Response("{}", { status: 429 }) },
  "model missing": { ai: () => new Response("{}", { status: 404 }) },
  "not JSON": { ai: aiSays("hello") },
  "score out of range": { ai: aiSays({ score: 400, tier: "A", reason: "x" }) },
  "too slow": { ai: (init) => new Promise((_, reject) => init.signal.addEventListener("abort", () => reject(init.signal.reason))) },
  "no key": { env: { GEMINI_API_KEY: "" } },
})) {
  test(`AI ${name}: written rules score it instead`, async () => {
    const keepAlive = setTimeout(() => {}, 500);
    const { send, calls } = setup(options);
    const { status, json } = await send(GOOD);
    clearTimeout(keepAlive);
    assert.equal(status, 200);
    assert.equal(json.scored_by, "rules");
    assert.equal(json.tier, "A");
    assert.ok(calls.logs[0].payload.ai_error);
  });
}

test("repeat enquiry updates the same record and keeps earlier answers", async () => {
  const rows = [{ id: "old", email: "priya@northwind.example", company: "Northwind", role: "Head of Operations", status: "new" }];
  const { send, calls } = setup({ rows });
  const { json } = await send({ email: "PRIYA@northwind.example", use_case: "follow up", role: "" });
  assert.equal(json.is_duplicate, true);
  assert.equal(json.lead_id, "old");
  assert.equal(calls.leads.length, 1);
  assert.equal(calls.leads[0].role, "Head of Operations");
  assert.equal(calls.leads[0].status, "new");
});

test("two saves at the same moment still give one record", async () => {
  const { send, calls } = setup({ conflictOnce: true });
  const { json } = await send(GOOD);
  assert.equal(json.is_duplicate, true);
  assert.equal(calls.leads.length, 1);
});

test("bad email or unreadable body gives 422 and logs no address", async () => {
  for (const payload of [{ email: "not-an-email" }, {}, "{broken", { email: "a@b.com", use_case: "x".repeat(30000) }]) {
    const { send, calls } = setup();
    assert.equal((await send(payload)).status, 422);
    assert.equal(calls.leads.length, 0);
    assert.equal(calls.logs[0].event, "submission_failed");
    assert.ok(!JSON.stringify(calls.logs).includes("not-an-email"));
  }
});

test("unknown dropdown values are dropped", async () => {
  const { send, calls } = setup();
  await send({ ...GOOD, company_size: "huge", timeline: "toString" });
  assert.equal(calls.leads[0].company_size, null);
  assert.equal(calls.leads[0].timeline, null);
});

test("database down gives 500 so Make can raise the alarm", async () => {
  const { send, calls } = setup({ dbDown: true });
  assert.equal((await send(GOOD)).status, 500);
  assert.equal(calls.logs[0].event, "submission_failed");
});
