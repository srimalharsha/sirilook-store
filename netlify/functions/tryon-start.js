exports.handler = async (event) => {
  const headers = { "content-type": "application/json", "cache-control": "no-store" };
  if (event.httpMethod === "OPTIONS") return { statusCode: 204, headers, body: "" };
  if (event.httpMethod !== "POST") return { statusCode: 405, headers, body: JSON.stringify({ error: "POST only" }) };

  const apiKey = process.env.FASHN_API_KEY;
  if (!apiKey) return { statusCode: 503, headers, body: JSON.stringify({ error: "AI try-on is not configured yet. Add FASHN_API_KEY in Netlify environment variables." }) };

  try {
    const body = JSON.parse(event.body || "{}");
    const modelImage = String(body.modelImage || "");
    const garmentImage = String(body.productImage || "");
    const category = ["auto", "tops", "bottoms", "one-pieces"].includes(body.category) ? body.category : "auto";
    if (!/^data:image\/(jpeg|jpg|png|webp);base64,/i.test(modelImage)) throw new Error("Please upload a JPG, PNG, or WebP customer photo.");
    if (!/^https:\/\//i.test(garmentImage)) throw new Error("Product image URL must use HTTPS.");
    if (modelImage.length > 14 * 1024 * 1024) throw new Error("Customer photo is too large. Please choose a photo under 10 MB.");

    const response = await fetch("https://api.fashn.ai/v1/run", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({
        model_name: "tryon-max",
        inputs: {
          model_image: modelImage,
          garment_image: garmentImage,
          category,
          mode: "balanced",
          output_format: "png"
        }
      })
    });
    const data = await response.json();
    if (!response.ok || !data.id) throw new Error(data.error?.message || data.error || "Unable to start AI try-on.");
    return { statusCode: 200, headers, body: JSON.stringify({ id: data.id }) };
  } catch (error) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: error.message || "AI try-on failed." }) };
  }
};
