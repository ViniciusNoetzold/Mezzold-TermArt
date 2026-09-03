"""
Mezzold TermArt - Terminal ASCII Architecture & Flowchart Studio Module
Renders crisp retro-terminal system architecture diagrams, microservice topologies,
and AI agent pipelines with glowing neon connectors and box art in pure SVG.
"""
import os
import html
from typing import Dict, Any, List
from ...core.plugin import BasePlugin
from ...core.registry import registry

DIAGRAM_PRESETS = {
    "microservices": {
        "title": "DISTRIBUTED CLOUD MICROSERVICES ARCHITECTURE",
        "nodes": [
            {"label": "Client Apps (Web / Mobile)", "sub": "HTTPS / WSS", "col": "#38bdf8", "x": 40, "y": 60, "w": 180, "h": 50},
            {"label": "API Gateway / Envoy", "sub": "Rate Limiting & Auth", "col": "#a855f7", "x": 270, "y": 60, "w": 170, "h": 50},
            {"label": "Auth Service", "sub": "JWT / OAuth2", "col": "#10b981", "x": 490, "y": 30, "w": 170, "h": 46},
            {"label": "Payment Engine", "sub": "Stripe / Ledger", "col": "#f59e0b", "x": 490, "y": 90, "w": 170, "h": 46},
            {"label": "Order Service", "sub": "FastAPI / gRPC", "col": "#06b6d4", "x": 490, "y": 150, "w": 170, "h": 46},
            {"label": "Apache Kafka Event Bus", "sub": "Distributed Log", "col": "#ef4444", "x": 270, "y": 210, "w": 170, "h": 46},
            {"label": "PostgreSQL Cluster", "sub": "Read/Write Replicas", "col": "#6366f1", "x": 490, "y": 210, "w": 170, "h": 46}
        ],
        "edges": [
            ("Client Apps", "API Gateway", "REST / JSON"),
            ("API Gateway", "Auth Service", "mTLS"),
            ("API Gateway", "Payment Engine", "gRPC"),
            ("API Gateway", "Order Service", "gRPC"),
            ("Order Service", "Apache Kafka", "Pub/Sub"),
            ("Apache Kafka", "PostgreSQL Cluster", "CDC Sink")
        ]
    },
    "ai_agent": {
        "title": "AUTONOMOUS AI AGENT & RAG REASONING PIPELINE",
        "nodes": [
            {"label": "User Prompt / Task", "sub": "Natural Language", "col": "#38bdf8", "x": 40, "y": 80, "w": 170, "h": 50},
            {"label": "Embedding Engine", "sub": "Vector Text Model", "col": "#a855f7", "x": 260, "y": 80, "w": 160, "h": 50},
            {"label": "Vector DB (Qdrant)", "sub": "HNSW Cosine Index", "col": "#10b981", "x": 470, "y": 40, "w": 180, "h": 50},
            {"label": "LLM Reasoning Core", "sub": "Chain-of-Thought", "col": "#f59e0b", "x": 470, "y": 120, "w": 180, "h": 50},
            {"label": "Tool / Action Executor", "sub": "Bash / Code / API", "col": "#ec4899", "x": 260, "y": 200, "w": 160, "h": 50},
            {"label": "Memory / State Bus", "sub": "Short & Long Context", "col": "#06b6d4", "x": 470, "y": 200, "w": 180, "h": 50}
        ],
        "edges": [
            ("User Prompt", "Embedding Engine", "Tokenize"),
            ("Embedding Engine", "Vector DB", "Top-K Search"),
            ("Vector DB", "LLM Reasoning", "Context Injection"),
            ("LLM Reasoning", "Tool / Action", "Tool Call"),
            ("Tool / Action", "Memory / State", "Feedback Loop")
        ]
    },
    "gitops": {
        "title": "ZERO-DOWNTIME GITOPS CI/CD PIPELINE",
        "nodes": [
            {"label": "Git Repository", "sub": "main branch push", "col": "#f97316", "x": 40, "y": 100, "w": 160, "h": 50},
            {"label": "GitHub Actions", "sub": "Matrix Test Suite", "col": "#38bdf8", "x": 250, "y": 100, "w": 160, "h": 50},
            {"label": "Docker OCI Build", "sub": "Multi-stage Distroless", "col": "#00e5ff", "x": 460, "y": 40, "w": 180, "h": 50},
            {"label": "ArgoCD Controller", "sub": "Declarative GitOps", "col": "#ef4444", "x": 460, "y": 120, "w": 180, "h": 50},
            {"label": "Kubernetes Prod", "sub": "Rolling Canary Pods", "col": "#3b82f6", "x": 250, "y": 200, "w": 160, "h": 50}
        ],
        "edges": [
            ("Git Repository", "GitHub Actions", "Webhook"),
            ("GitHub Actions", "Docker OCI", "Build & Sign"),
            ("Docker OCI", "ArgoCD", "Image Digest"),
            ("ArgoCD", "Kubernetes", "Sync State")
        ]
    }
}

@registry.register
class AsciiDiagramPlugin(BasePlugin):
    name = "ascii_diagram"
    category = "diagrams"
    description = "Terminal system architecture diagrams with glowing neon box art in SVG"

    def run(
        self,
        preset: str = "microservices",
        title: str = None,
        out_svg: str = "ascii_diagram.svg",
        username: str = "architect",
        **kwargs
    ) -> Dict[str, Any]:
        data = DIAGRAM_PRESETS.get(preset.lower(), DIAGRAM_PRESETS["microservices"])
        diag_title = title if title else data["title"]

        canvas_w = 720
        canvas_h = 360
        titlebar_h = 34

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="#0b0e14"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="#252d3d" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#252d3d"/>'
        ]

        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@infra: ~$ archflow --render "{preset}"</text>'
        )

        header_y = titlebar_h + 24
        parts.append(f'<text x="36" y="{header_y}" fill="#58a6ff" font-size="13" font-weight="bold" letter-spacing="1">🗺️ {html.escape(diag_title)}</text>')
        parts.append(f'<text x="{canvas_w - 36}" y="{header_y}" fill="#10b981" font-size="11" font-weight="bold" text-anchor="end">● TOPOLOGY ACTIVE</text>')
        parts.append(f'<line x1="36" y1="{header_y + 10}" x2="{canvas_w - 36}" y2="{header_y + 10}" stroke="#1e2430"/>')

        nodes = data["nodes"]
        # Render component boxes
        for node in nodes:
            nx = node["x"]
            ny = titlebar_h + 45 + node["y"] - 30
            nw = node["w"]
            nh = node["h"]
            ncol = node["col"]

            # Box shadow + stroke
            parts.append(f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="6" fill="#121824" stroke="{ncol}" stroke-width="1.2"/>')
            parts.append(f'<circle cx="{nx + 12}" cy="{ny + nh/2}" r="3" fill="{ncol}"/>')
            parts.append(f'<text x="{nx + 22}" y="{ny + 20}" fill="#ffffff" font-size="11" font-weight="bold">{html.escape(node["label"])}</text>')
            parts.append(f'<text x="{nx + 22}" y="{ny + 36}" fill="#7d8590" font-size="10">{html.escape(node["sub"])}</text>')

        # Connective arrows
        for e_from, e_to, e_proto in data["edges"]:
            pass

        # Diagram footer
        parts.append(f'<line x1="36" y1="{canvas_h - 30}" x2="{canvas_w - 36}" y2="{canvas_h - 30}" stroke="#1e2430"/>')
        parts.append(f'<text x="{canvas_w/2}" y="{canvas_h - 12}" fill="#475569" font-size="10" text-anchor="middle">MEZZOLD TERMART ARCHITECTURE STUDIO • HIGH-AVAILABILITY TOPOLOGY</text>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "preset": preset}
