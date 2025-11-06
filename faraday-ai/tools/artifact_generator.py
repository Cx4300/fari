"""
FARADAY AI - Artifact Generator Tool
Claude-style artifact generation (React components, documents, charts, etc.)
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from tools.function_registry import register_function
from config.settings import settings
from utils.logger import logger
from engines.llm_engine import get_llm_engine


ARTIFACT_TYPES = {
    "react": "React component (JSX/TSX)",
    "html": "HTML document",
    "svg": "SVG graphic",
    "mermaid": "Mermaid diagram",
    "chart": "Chart.js or similar chart",
    "document": "Markdown document",
    "presentation": "Markdown presentation (reveal.js)",
    "code": "Code snippet (any language)",
}


@register_function(
    name="generate_artifact",
    description="Generate artifacts like React components, HTML pages, SVG graphics, diagrams, charts, documents, or presentations. Returns the generated artifact code.",
    parameters={
        "type": "object",
        "properties": {
            "artifact_type": {
                "type": "string",
                "description": f"Type of artifact to generate. Options: {', '.join(ARTIFACT_TYPES.keys())}",
                "enum": list(ARTIFACT_TYPES.keys())
            },
            "prompt": {
                "type": "string",
                "description": "Description of what to generate"
            },
            "title": {
                "type": "string",
                "description": "Title for the artifact (optional)"
            }
        },
        "required": ["artifact_type", "prompt"]
    }
)
async def generate_artifact(
    artifact_type: str,
    prompt: str,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate artifacts (React components, documents, charts, etc.).

    Args:
        artifact_type: Type of artifact (react, html, svg, mermaid, chart, document, presentation, code)
        prompt: Description of what to generate
        title: Optional title

    Returns:
        Generated artifact with code and metadata
    """
    try:
        logger.info(f"🎨 Generating {artifact_type} artifact: {prompt[:50]}...")

        if artifact_type not in ARTIFACT_TYPES:
            return {
                "success": False,
                "error": f"Unknown artifact type: {artifact_type}. Valid types: {', '.join(ARTIFACT_TYPES.keys())}"
            }

        # Get LLM engine
        llm = get_llm_engine()

        # Generate system prompt based on artifact type
        system_prompt = _get_system_prompt_for_type(artifact_type)

        # Generate artifact
        generation_prompt = f"""Generate a {ARTIFACT_TYPES[artifact_type]} based on this request:

{prompt}

{f'Title: {title}' if title else ''}

Requirements:
- Generate ONLY the code/content, no explanations
- Make it production-ready and well-structured
- Include comments where appropriate
- Follow best practices for {artifact_type}

Generated {artifact_type}:
```"""

        generated_code = ""
        async for chunk in llm.generate(generation_prompt, system_prompt, stream=True):
            generated_code += chunk

        # Clean up code (remove markdown code blocks if present)
        generated_code = _clean_generated_code(generated_code)

        # Save artifact
        artifact_id = _generate_artifact_id()
        artifact_path = await _save_artifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            code=generated_code,
            prompt=prompt,
            title=title
        )

        logger.info(f"✅ Artifact generated: {artifact_id}")

        return {
            "success": True,
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "title": title or f"{artifact_type.title()} Artifact",
            "code": generated_code,
            "file_path": str(artifact_path),
            "metadata": {
                "type": artifact_type,
                "type_description": ARTIFACT_TYPES[artifact_type],
                "prompt": prompt,
                "generated_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"❌ Artifact generation error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def _get_system_prompt_for_type(artifact_type: str) -> str:
    """Get system prompt for artifact type"""

    prompts = {
        "react": """You are an expert React developer. Generate clean, modern React components using functional components and hooks. Use TypeScript when appropriate. Follow React best practices.""",

        "html": """You are an expert web developer. Generate clean, semantic HTML5 code with proper structure. Include inline CSS for styling if needed.""",

        "svg": """You are an expert SVG designer. Generate clean, optimized SVG graphics. Use proper viewBox, and make graphics scalable and accessible.""",

        "mermaid": """You are an expert in creating Mermaid diagrams. Generate clear, well-structured diagrams (flowcharts, sequence diagrams, etc.).""",

        "chart": """You are an expert in data visualization. Generate chart configurations (Chart.js, D3.js, etc.) that are clear and informative.""",

        "document": """You are an expert technical writer. Generate well-structured Markdown documents with proper headings, formatting, and organization.""",

        "presentation": """You are an expert at creating presentations. Generate Markdown presentations for reveal.js with clear slides and good visual hierarchy.""",

        "code": """You are an expert programmer. Generate clean, well-commented code following best practices for the requested programming language.""",
    }

    return prompts.get(artifact_type, "You are a helpful AI assistant.")


def _clean_generated_code(code: str) -> str:
    """Clean up generated code (remove markdown fences, etc.)"""
    # Remove markdown code blocks
    if "```" in code:
        lines = code.split('\n')
        in_code_block = False
        cleaned_lines = []

        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block or not line.strip().startswith("```"):
                cleaned_lines.append(line)

        code = '\n'.join(cleaned_lines)

    return code.strip()


def _generate_artifact_id() -> str:
    """Generate unique artifact ID"""
    from datetime import datetime
    import hashlib

    timestamp = datetime.now().isoformat()
    return hashlib.md5(timestamp.encode()).hexdigest()[:12]


async def _save_artifact(
    artifact_id: str,
    artifact_type: str,
    code: str,
    prompt: str,
    title: Optional[str]
) -> Path:
    """Save artifact to disk"""
    # Determine file extension
    extensions = {
        "react": ".jsx",
        "html": ".html",
        "svg": ".svg",
        "mermaid": ".mmd",
        "chart": ".json",
        "document": ".md",
        "presentation": ".md",
        "code": ".txt",
    }

    ext = extensions.get(artifact_type, ".txt")
    filename = f"{artifact_id}_{artifact_type}{ext}"
    artifact_path = settings.artifacts_dir / filename

    # Save code
    artifact_path.write_text(code, encoding='utf-8')

    # Save metadata
    metadata = {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "title": title,
        "prompt": prompt,
        "created_at": datetime.now().isoformat(),
        "file_path": str(artifact_path)
    }

    metadata_path = settings.artifacts_dir / f"{artifact_id}_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')

    logger.info(f"💾 Artifact saved: {artifact_path}")

    return artifact_path


# Export
__all__ = ['generate_artifact', 'ARTIFACT_TYPES']
