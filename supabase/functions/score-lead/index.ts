// Entry point on Supabase (Deno). The logic lives in handler.ts.
import { createHandler } from "./handler.ts";
import icp from "./icp.json" with { type: "json" };

Deno.serve(createHandler({ env: (name) => Deno.env.get(name), fetch, icp }));
