"""
Mezzold TermArt - Terminal ASCII Architecture & Flowchart Studio Module
Renders crisp retro-terminal system architecture diagrams, microservice topologies,
and AI agent pipelines with glowing neon connectors, animated data streams, and box art in pure SVG.
"""
import os
import html
from typing import Dict, Any, List, Optional
from ...core.plugin import BasePlugin
from ...core.registry import registry

DIAGRAM_PRESETS = {
    "microservices": {
        "title": "DISTRIBUTED CLOUD MICROSERVICES TOPOLOGY",
        "subtitle": "KUBERNETES • ENVOY GATEWAY • EVENT-DRIVEN CQRS",
        "nodes": [
            {"id": "clients", "label": "Client Apps & Web", "sub": "HTTPS / WSS / GraphQL", "col": "#38bdf8", "x": 40, "y": 120, "w": 180, "h": 52},
            {"id": "gateway", "label": "API Gateway / Envoy", "sub": "Rate Limit • Auth • TLS", "col": "#a855f7", "x": 280, "y": 70, "w": 180, "h": 52},
            {"id": "kafka", "label": "Apache Kafka Event Bus", "sub": "Distributed Commit Log", "col": "#ef4444", "x": 280, "y": 240, "w": 180, "h": 52},
            {"id": "auth", "label": "Auth & Identity Core", "sub": "OAuth2 / JWT Token / mTLS", "col": "#10b981", "x": 540, "y": 40, "w": 195, "h": 50},
            {"id": "payment", "label": "Payment & Order Engine", "sub": "FastAPI / gRPC Service", "col": "#f59e0b", "x": 540, "y": 115, "w": 195, "h": 50},
            {"id": "worker", "label": "Analytics & AI Worker", "sub": "Async Stream Consumer", "col": "#06b6d4", "x": 540, "y": 205, "w": 195, "h": 50},
            {"id": "postgres", "label": "PostgreSQL & Redis DB", "sub": "HA Cluster • Read Replicas", "col": "#6366f1", "x": 540, "y": 285, "w": 195, "h": 50}
        ],
        "edges": [
            ("clients", "gateway", "REST / WSS", "#38bdf8"),
            ("gateway", "auth", "mTLS Verify", "#10b981"),
            ("gateway", "payment", "gRPC / HTTP2", "#f59e0b"),
            ("payment", "kafka", "Pub/Sub Event", "#ef4444"),
            ("kafka", "worker", "Consumer Group", "#06b6d4"),
            ("kafka", "postgres", "CDC Sink", "#6366f1")
        ]
    },
    "ai_agent": {
        "title": "AUTONOMOUS AI AGENT SWARM & RAG PIPELINE",
        "subtitle": "REASONING CORE • VECTOR INDEX • CODE INTERPRETER",
        "nodes": [
            {"id": "user", "label": "User Query / Goal", "sub": "Natural Language Task", "col": "#38bdf8", "x": 40, "y": 120, "w": 180, "h": 52},
            {"id": "embed", "label": "Embedding Encoder", "sub": "Dense Vectorization", "col": "#a855f7", "x": 280, "y": 60, "w": 180, "h": 52},
            {"id": "tools", "label": "Tool / Action Executor", "sub": "Bash • Python • REST API", "col": "#ec4899", "x": 280, "y": 230, "w": 180, "h": 52},
            {"id": "vectordb", "label": "Vector DB (Qdrant)", "sub": "HNSW Cosine Similarity", "col": "#10b981", "x": 540, "y": 40, "w": 195, "h": 50},
            {"id": "llm", "label": "LLM Reasoning Swarm", "sub": "Chain-of-Thought / ReAct", "col": "#f59e0b", "x": 540, "y": 125, "w": 195, "h": 52},
            {"id": "memory", "label": "Memory & State Bus", "sub": "Episodic & Working Memory", "col": "#06b6d4", "x": 540, "y": 230, "w": 195, "h": 50}
        ],
        "edges": [
            ("user", "embed", "Tokenize", "#38bdf8"),
            ("embed", "vectordb", "Top-K Vector", "#10b981"),
            ("vectordb", "llm", "Context Embed", "#10b981"),
            ("llm", "tools", "Tool Call", "#ec4899"),
            ("tools", "memory", "Exec Feedback", "#ec4899"),
            ("memory", "llm", "State Update", "#06b6d4")
        ]
    },
    "gitops": {
        "title": "ZERO-DOWNTIME GITOPS CI/CD PIPELINE",
        "subtitle": "DECLARATIVE STATE • CANARY ROLLOUTS • COSMIC OBSERVABILITY",
        "nodes": [
            {"id": "git", "label": "Git Repository (main)", "sub": "Signed Commits & PRs", "col": "#f97316", "x": 40, "y": 120, "w": 180, "h": 52},
            {"id": "ci", "label": "GitHub Actions CI", "sub": "Matrix Test & SAST Lint", "col": "#38bdf8", "x": 280, "y": 60, "w": 180, "h": 52},
            {"id": "argocd", "label": "ArgoCD Controller", "sub": "Declarative State Reconciler", "col": "#ef4444", "x": 280, "y": 230, "w": 180, "h": 52},
            {"id": "registry", "label": "OCI Distroless Registry", "sub": "Cosign Signature • SBOM", "col": "#00e5ff", "x": 540, "y": 60, "w": 195, "h": 50},
            {"id": "k8s", "label": "Kubernetes Prod Cluster", "sub": "Rolling Canary Deployments", "col": "#3b82f6", "x": 540, "y": 160, "w": 195, "h": 50},
            {"id": "prom", "label": "Prometheus & Grafana", "sub": "SLO Radar & Auto-Rollback", "col": "#10b981", "x": 540, "y": 260, "w": 195, "h": 50}
        ],
        "edges": [
            ("git", "ci", "Push Webhook", "#f97316"),
            ("ci", "registry", "Build & Cosign", "#00e5ff"),
            ("registry", "argocd", "Image Digest", "#ef4444"),
            ("argocd", "k8s", "Sync Manifest", "#3b82f6"),
            ("k8s", "prom", "Metrics / Telemetry", "#10b981")
        ]
    },
    "event_driven": {
        "title": "REAL-TIME EVENT-DRIVEN & CQRS ARCHITECTURE",
        "subtitle": "WEBSOCKETS • NATS JETSTREAM • MATERIALIZED VIEWS",
        "nodes": [
            {"id": "clients", "label": "Web & Mobile Clients", "sub": "Bidirectional Realtime", "col": "#38bdf8", "x": 40, "y": 120, "w": 180, "h": 52},
            {"id": "ingress", "label": "Ingress & Edge Proxy", "sub": "TLS Term • Protocol Buffer", "col": "#a855f7", "x": 280, "y": 60, "w": 180, "h": 52},
            {"id": "nats", "label": "NATS JetStream Bus", "sub": "Low Latency Pub/Sub", "col": "#f59e0b", "x": 280, "y": 230, "w": 180, "h": 52},
            {"id": "command", "label": "Command Handler", "sub": "CQRS Write Aggregate", "col": "#ec4899", "x": 540, "y": 50, "w": 195, "h": 50},
            {"id": "eventstore", "label": "Event Sourcing Store", "sub": "Append-Only Immutable Log", "col": "#10b981", "x": 540, "y": 145, "w": 195, "h": 50},
            {"id": "cache", "label": "Redis Read Cache", "sub": "Materialized Query Projections", "col": "#06b6d4", "x": 540, "y": 240, "w": 195, "h": 50}
        ],
        "edges": [
            ("clients", "ingress", "WSS / HTTP3", "#38bdf8"),
            ("ingress", "command", "Write Command", "#ec4899"),
            ("command", "nats", "Publish Event", "#f59e0b"),
            ("nats", "eventstore", "Persist Log", "#10b981"),
            ("nats", "cache", "Update View", "#06b6d4")
        ]
    }
}

@registry.register
class AsciiDiagramPlugin(BasePlugin):
    name = "ascii_diagram"
    category = "diagrams"
    description = "Terminal system architecture diagrams with glowing neon box art and animated bus connectors in SVG"

    def run(
        self,
        preset: str = "microservices",
        title: Optional[str] = None,
        out_svg: str = "ascii_diagram.svg",
        username: str = "architect",
        **kwargs
    ) -> Dict[str, Any]:
        preset_key = preset.lower() if preset else "microservices"
        data = DIAGRAM_PRESETS.get(preset_key, DIAGRAM_PRESETS["microservices"])
        diag_title = title if title else data["title"]
        diag_subtitle = data.get("subtitle", "SYSTEM TOPOLOGY & LIVE TRAFFIC")

        canvas_w = 820
        canvas_h = 440
        titlebar_h = 34

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
            # Defs for grid and markers
            '<defs>',
            '  <pattern id="diag-grid" width="24" height="24" patternUnits="userSpaceOnUse">',
            '    <circle cx="2" cy="2" r="0.8" fill="#1e293b" opacity="0.65"/>',
            '  </pattern>',
            '</defs>',
            # Background
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="14" fill="#080b11"/>',
            f'<rect width="{canvas_w}" height="{canvas_h}" rx="14" fill="url(#diag-grid)"/>',
            f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="14" fill="none" stroke="#1e293b" stroke-width="1"/>',
            f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="#1e293b"/>'
        ]

        # macOS traffic lights
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
            parts.append(f'<circle cx="{18 + i*16}" cy="{titlebar_h/2}" r="5" fill="{c}"/>')

        # Titlebar terminal prompt
        parts.append(
            f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="#7d8590" font-size="12" '
            f'text-anchor="middle">{username}@cluster: ~$ kubectl get topology --live-stream --preset={html.escape(preset_key)}</text>'
        )

        header_y = titlebar_h + 24
        parts.append(f'<text x="32" y="{header_y}" fill="#38bdf8" font-size="13" font-weight="bold" letter-spacing="1">🗺️ {html.escape(diag_title)}</text>')
        parts.append(f'<text x="32" y="{header_y + 16}" fill="#64748b" font-size="9.5" font-weight="600" letter-spacing="0.5">{html.escape(diag_subtitle)}</text>')
        
        # Live status badge
        parts.append(f'<rect x="{canvas_w - 170}" y="{header_y - 12}" width="138" height="22" rx="11" fill="#062817" stroke="#10b981" stroke-width="1"/>')
        parts.append(f'<circle cx="{canvas_w - 156}" cy="{header_y - 1}" r="3.5" fill="#10b981"><animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/></circle>')
        parts.append(f'<text x="{canvas_w - 146}" y="{header_y + 2.5}" fill="#34d399" font-size="9.5" font-weight="bold">TOPOLOGY ONLINE</text>')

        parts.append(f'<line x1="32" y1="{header_y + 26}" x2="{canvas_w - 32}" y2="{header_y + 26}" stroke="#1a2233"/>')

        nodes = data["nodes"]
        node_map = {}
        for n in nodes:
            # Match by id or label
            node_map[n.get("id", "")] = n
            node_map[n["label"].lower()] = n

        def resolve_node(ref: str) -> Optional[Dict[str, Any]]:
            ref_low = ref.lower()
            if ref_low in node_map:
                return node_map[ref_low]
            for k, val in node_map.items():
                if ref_low in k:
                    return val
            return None

        # Y offset for nodes inside canvas
        y_shift = titlebar_h + 38

        # Render CONNECTORS (behind nodes so box ports look crisp)
        for edge_spec in data["edges"]:
            if len(edge_spec) >= 4:
                src_id, dst_id, proto, edge_col = edge_spec[0], edge_spec[1], edge_spec[2], edge_spec[3]
            else:
                src_id, dst_id, proto = edge_spec[0], edge_spec[1], edge_spec[2]
                edge_col = "#38bdf8"

            s_node = resolve_node(src_id)
            d_node = resolve_node(dst_id)
            if not s_node or not d_node:
                continue

            sx = s_node["x"]
            sy = s_node["y"] + y_shift
            sw = s_node["w"]
            sh = s_node["h"]

            dx = d_node["x"]
            dy = d_node["y"] + y_shift
            dw = d_node["w"]
            dh = d_node["h"]

            # Compute ports
            if dx >= sx + sw - 10:
                # Target is to the right
                start = (sx + sw, sy + sh / 2)
                end = (dx, dy + dh / 2)
                delta_x = max(35, (end[0] - start[0]) * 0.45)
                c1 = (start[0] + delta_x, start[1])
                c2 = (end[0] - delta_x, end[1])
                path_d = f"M {start[0]:.1f} {start[1]:.1f} C {c1[0]:.1f} {c1[1]:.1f}, {c2[0]:.1f} {c2[1]:.1f}, {end[0]:.1f} {end[1]:.1f}"
                mid_x = (start[0] + c1[0]*3 + c2[0]*3 + end[0]) / 8
                mid_y = (start[1] + c1[1]*3 + c2[1]*3 + end[1]) / 8
            elif dx + dw <= sx + 10:
                # Target is to the left
                start = (sx, sy + sh / 2)
                end = (dx + dw, dy + dh / 2)
                delta_x = max(35, (start[0] - end[0]) * 0.45)
                c1 = (start[0] - delta_x, start[1])
                c2 = (end[0] + delta_x, end[1])
                path_d = f"M {start[0]:.1f} {start[1]:.1f} C {c1[0]:.1f} {c1[1]:.1f}, {c2[0]:.1f} {c2[1]:.1f}, {end[0]:.1f} {end[1]:.1f}"
                mid_x = (start[0] + c1[0]*3 + c2[0]*3 + end[0]) / 8
                mid_y = (start[1] + c1[1]*3 + c2[1]*3 + end[1]) / 8
            else:
                # Vertical connection
                start = (sx + sw / 2, sy + sh)
                end = (dx + dw / 2, dy)
                path_d = f"M {start[0]:.1f} {start[1]:.1f} L {end[0]:.1f} {end[1]:.1f}"
                mid_x = (start[0] + end[0]) / 2
                mid_y = (start[1] + end[1]) / 2

            # 1. Base dark bus line
            parts.append(f'<path d="{path_d}" fill="none" stroke="#1c2536" stroke-width="3" stroke-linecap="round"/>')

            # 2. Glowing animated data pulses
            parts.append(
                f'<path d="{path_d}" fill="none" stroke="{edge_col}" stroke-width="1.8" '
                f'stroke-dasharray="6,8" stroke-linecap="round" opacity="0.85">'
                f'<animate attributeName="stroke-dashoffset" from="28" to="0" dur="1.2s" repeatCount="indefinite"/>'
                f'</path>'
            )

            # 3. Connection port indicator dots
            parts.append(f'<circle cx="{start[0]:.1f}" cy="{start[1]:.1f}" r="3" fill="{edge_col}"/>')
            parts.append(f'<circle cx="{end[0]:.1f}" cy="{end[1]:.1f}" r="3" fill="{edge_col}"/>')

            # 4. Protocol Badge Pill
            pw = len(proto) * 7 + 18
            parts.append(f'<rect x="{mid_x - pw/2:.1f}" y="{mid_y - 9.5:.1f}" width="{pw}" height="19" rx="5" fill="#080c14" stroke="{edge_col}" stroke-width="1.1" opacity="0.95"/>')
            parts.append(f'<text x="{mid_x:.1f}" y="{mid_y + 3.5:.1f}" fill="{edge_col}" font-size="9" font-family="monospace" text-anchor="middle" font-weight="bold">{html.escape(proto)}</text>')

        # Render COMPONENT BOXES
        for node in nodes:
            nx = node["x"]
            ny = node["y"] + y_shift
            nw = node["w"]
            nh = node["h"]
            ncol = node["col"]

            # Background box with glow border
            parts.append(f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="8" fill="#0e1422" stroke="{ncol}" stroke-width="1.4" opacity="0.98"/>')
            # Top highlight line
            parts.append(f'<line x1="{nx+8}" y1="{ny+1}" x2="{nx+nw-8}" y2="{ny+1}" stroke="{ncol}" stroke-width="1" opacity="0.6"/>')

            # Blinking status indicator
            parts.append(f'<circle cx="{nx + 14}" cy="{ny + nh/2}" r="3.5" fill="{ncol}">')
            parts.append(f'  <animate attributeName="opacity" values="1;0.4;1" dur="2s" repeatCount="indefinite"/>')
            parts.append(f'</circle>')

            # Box Labels
            parts.append(f'<text x="{nx + 25}" y="{ny + 21}" fill="#ffffff" font-size="11" font-weight="bold">{html.escape(node["label"])}</text>')
            parts.append(f'<text x="{nx + 25}" y="{ny + 37}" fill="#94a3b8" font-size="9.5">{html.escape(node["sub"])}</text>')

        # Diagram footer
        parts.append(f'<line x1="32" y1="{canvas_h - 28}" x2="{canvas_w - 32}" y2="{canvas_h - 28}" stroke="#1a2233"/>')
        parts.append(f'<text x="36" y="{canvas_h - 12}" fill="#475569" font-size="9.5">STATUS: HIGH AVAILABILITY • LATENCY: &lt;14ms • REPLICAS: 3/3</text>')
        parts.append(f'<text x="{canvas_w - 36}" y="{canvas_h - 12}" fill="#475569" font-size="9.5" text-anchor="end">MEZZOLD TERMART ARCHITECTURE STUDIO</text>')

        parts.append('</svg>')
        svg_content = "".join(parts)

        if out_svg:
            os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
            with open(out_svg, "w", encoding="utf-8") as f:
                f.write(svg_content)

        return {"status": "success", "output_path": out_svg, "preset": preset_key}
