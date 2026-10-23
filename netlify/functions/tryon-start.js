exports.handler = async (event) => {
  const headers = { "content-type": "application/json", "access-control-allow-origin": "*" };
  if (event.httpMethod === "OPTIONS") return { statusCode: 204, headers, body: "" };
  if (event.httpMethod !== "POST") return { statusCode: 405, headers, body: JSON.stringify({ error: "POST only" }) };

  const apiKey = process.env.FASHN_API_KEY;
  if (!apiKey) return { statusCode: 503, headers, body: JSON.stringify({ error: "AI try-on is not configured yet. Add FASHN_API_KEY in Netlify environment variables." }) };

  try {
    const body = JSON.parse(event.body || "{}");
    const modelImage = String(body.modelImage || "");
    const productImage = String(body.productImage || "");
    const category = ["auto", "tops", "bottoms", "one-pieces"].includes(body.category) ? body.category : "auto";
    const prompt = String(body.prompt || "").slice(0, 500);
    if (!modelImage.startsWith("data:image/")) throw new Error("Please upload a valid customer photo.");
    if (!/^https?:\/\//i.test(productImage)) throw new Error("Product image URL is invalid.");
    if (modelImage.length > 30 * 1024 * 1024) throw new Error("Customer photo is too large.");

    const response = await fetch("https://api.fashn.ai/v1/run", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({
        model_name: "tryon-max",
        inputs: { model_image: modelImage, product_image: productImage, prompt, resolution: "1k", generation_mode: "fast", category, output_format: "jpeg", return_base64: true }
      })
    });
    const data = await response.json();
    if (!response.ok || !data.id) throw new Error(data.error?.message || data.error || "Unable to start AI try-on.");
    return { statusCode: 200, headers, body: JSON.stringify({ id: data.id }) };
  } catch (error) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: error.message || "AI try-on failed." }) };
  }
};
