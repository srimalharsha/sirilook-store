export default async (req) => {
  const headers = { "content-type": "application/json", "access-control-allow-origin": "*" };
  if (req.method === "OPTIONS") return new Response("", { status: 204, headers });
  const apiKey = process.env.FASHN_API_KEY;
  if (!apiKey) return new Response(JSON.stringify({ error: "AI try-on is not configured." }), { status: 503, headers });

  try {
    const url = new URL(req.url);
    const id = url.searchParams.get("id");
    if (!id) return new Response(JSON.stringify({ error: "Missing prediction id." }), { status: 400, headers });

    const response = await fetch(`https://api.fashn.ai/v1/status/${encodeURIComponent(id)}`, {
      headers: { Authorization: `Bearer ${apiKey}` }
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error?.message || data.error || "Unable to read AI try-on status.");

    return new Response(JSON.stringify({ status: data.status, output: data.output || [], error: data.error || null }), { status: 200, headers });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message || "AI status check failed." }), { status: 400, headers });
  }
};
