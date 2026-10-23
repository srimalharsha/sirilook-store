export default async (req) => {
  const headers = { "content-type": "application/json", "access-control-allow-origin": "*" };
  if (req.method === "OPTIONS") return new Response("", { status: 204, headers });
  if (req.method !== "POST") return new Response(JSON.stringify({ error: "POST only" }), { status: 405, headers });

  const apiKey = process.env.FASHN_API_KEY;
  if (!apiKey) return new Response(JSON.stringify({ error: "AI try-on is not configured yet. Add FASHN_API_KEY in Netlify environment variables." }), { status: 503, headers });

  try {
    const body = await req.json();
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
        inputs: {
          model_image: modelImage,
          product_image: productImage,
          prompt,
          resolution: "1k",
          generation_mode: "fast",
          category,
          output_format: "jpeg",
          return_base64: true
        }
      })
    });

    const data = await response.json();
    if (!response.ok || !data.id) throw new Error(data.error?.message || data.error || "Unable to start AI try-on.");
    return new Response(JSON.stringify({ id: data.id }), { status: 200, headers });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message || "AI try-on failed." }), { status: 400, headers });
  }
};
