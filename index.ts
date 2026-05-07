import express from "express"
import https from "https"
import fs from "fs"
import path from "path"
import { config } from "dotenv"

config();
const app = express()
app.use(express.json({ limit: "50mb" }))


const SSL_OPTIONS = {
    key: fs.readFileSync(path.join(__dirname, 'certs', 'server.key')),
    cert: fs.readFileSync(path.join(__dirname, 'certs', 'server.crt')),

    requestCert: true,
    rejectUnauthorized: true,

    ca: fs.readFileSync(path.join(__dirname, 'certs', 'ca.crt')),

    minVersion: 'TLSv1.2' as const,
    ciphers: [
        'ECDHE-RSA-AES256-GCM-SHA384',
        'ECDHE-RSA-AES128-GCM-SHA256',
    ].join(':'),
    honorCipherOrder: true
};

const HTTPS_PORT = 443;

const TARGET_SV = process.env.TARGET_SV! //  "http://0.0.0.0.0.0"
const TARGET_HEADER = process.env.TARGET_HEADER! //"some_auth_key"
const CLIENT_AUTH_HEADER = process.env.CLIENT_AUTH_HEADER! // "some_auth_key"

if (!TARGET_SV || !TARGET_HEADER || !CLIENT_AUTH_HEADER) throw new Error("Missing env variables!!");

app.use("/", async (req, res) => {
    if (!req.headers[CLIENT_AUTH_HEADER]) {
        return res.redirect(301, "https://www.microsoft.com/zh-cn")
    }

    try {
        const targetUrl = `${TARGET_SV}${req.originalUrl}`

        const headers: Record<string, string> = {}
        for (const [key, value] of Object.entries(req.headers)) {
            if (key !== "host" && typeof value === "string") {
                headers[key] = value
            }
        }
        headers[TARGET_HEADER] = "1"

        const fetchOptions: RequestInit = {
            method: req.method,
            headers,
        }

        if (["POST", "PUT", "PATCH"].includes(req.method) && req.body) {
            fetchOptions.body = JSON.stringify(req.body)
        }

        const response = await fetch(targetUrl, fetchOptions)

        response.headers.forEach((value, key) => {
            if (key !== "transfer-encoding" && key !== "content-encoding") {
                res.setHeader(key, value)
            }
        })

        res.status(response.status)
        const data = await response.text()
        res.send(data)

    } catch (err) {
        console.error("Proxy error:", err)
        res.status(502).json({ error: "Bad Gateway" })
    }
})

const httpsServer = https.createServer(SSL_OPTIONS, app)

httpsServer.listen(HTTPS_PORT, () => {
    console.log(`
╔════════════════════════════════════════════════════════════╗
║           MUTUAL TLS (mTLS) PROXY STARTED                  ║
╠════════════════════════════════════════════════════════════╣
║  Port: ${HTTPS_PORT}                                       ║
║  Protocol: HTTPS + mTLS                                    ║
║  Client Certificate: REQUIRED                              ║
║  Backend: ${TARGET_SV}                                     ║
╚════════════════════════════════════════════════════════════╝

    `)
})

httpsServer.on('tlsClientError', (err, socket) => {
    console.log(`[TLS ERROR] Client rejected: ${err.message}`);
});

process.on('SIGINT', () => {
    console.log('\nShutting down...')
    httpsServer.close(() => process.exit(0))
})
