// Test helper: reads people as JSON on stdin, prints the TypeScript scores.
import { readFileSync } from "node:fs";
import { scoreLead } from "../supabase/functions/score-lead/rules.ts";

const icp = JSON.parse(readFileSync(new URL("../supabase/functions/score-lead/icp.json", import.meta.url), "utf8"));
const people = JSON.parse(readFileSync(0, "utf8"));
console.log(JSON.stringify(people.map((p) => scoreLead(p, icp))));
