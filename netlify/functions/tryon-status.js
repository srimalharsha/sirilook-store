exports.handler = async (event) => {
  const headers = { "content-type": "application/json", "access-control-allow-origin": "*" };
  if (event.httpMethod === "OPTIONS") return { statusCode: 204, headers, body: "" };
  const apiKey = process.env.FASHN_API_KEY;
  if (!apiKey) return { statusCode: 503, headers, body: JSON.stringify({ error: "AI try-on is not configured." }) };
  try {
    const url = new URL(event.rawUrl || `https://${event.headers?.host || "localhost"}${event.path || ""}${event.rawQuery ? `?${event.rawQuery}` : ""}`);
    const id = url.searchParams.get("id");
    if (!id) return { statusCode: 400, headers, body: JSON.stringify({ error: "Missing prediction id." }) };
    const response = await fetch(`https://api.fashn.ai/v1/status/${encodeURIComponent(id)}`, { headers: { Authorization: `Bearer ${apiKey}` } });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error?.message || data.error || "Unable to read AI try-on status.");
    return { statusCode: 200, headers, body: JSON.stringify({ status: data.status, output: data.output || [], error: data.error || null }) };
  } catch (error) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: error.message || "AI status check failed." }) };
  }
};
