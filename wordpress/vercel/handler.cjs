const { handler } = require('serverlesswp/wordpress');

module.exports = async function wordpress(request, response) {
    try {
        const chunks = [];
        for await (const chunk of request) {
            chunks.push(chunk);
        }
        const result = await handler({
            path: request.url,
            httpMethod: request.method,
            headers: request.headers,
            body: Buffer.concat(chunks).toString('base64'),
            isBase64Encoded: true,
        });

        response.statusCode = result.statusCode;
        for (const [name, value] of Object.entries(result.headers || {})) {
            response.setHeader(name, value);
        }
        response.end(Buffer.from(result.body || '', result.isBase64Encoded ? 'base64' : 'utf8'));
    } catch (error) {
        console.error('WordPress request failed', error);
        response.statusCode = 500;
        response.end('WordPress is temporarily unavailable.');
    }
};
