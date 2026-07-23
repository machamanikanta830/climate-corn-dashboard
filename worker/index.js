export default {
  async fetch(request, env) {
    if (!env.ASSETS) {
      return new Response("Static asset binding is unavailable", { status: 503 });
    }

    const response = await env.ASSETS.fetch(request);
    const acceptsHtml = request.headers.get("accept")?.includes("text/html");
    if (response.status !== 404 || request.method !== "GET" || !acceptsHtml) {
      return response;
    }

    const indexUrl = new URL("/index.html", request.url);
    return env.ASSETS.fetch(new Request(indexUrl, request));
  },
};
