"""
FARADAY AI - Agent Engine
OpenAI Agents SDK for multi-step reasoning and tool orchestration
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
import json

from config.settings import settings
from utils.logger import logger
from engines.llm_engine import get_llm_engine


class AgentEngine:
    """
    Agent Engine for multi-step reasoning, planning, and tool orchestration.
    Implements a simple ReAct-style agent pattern.
    """

    def __init__(self):
        """Initialize Agent Engine"""
        self.config = settings.agent
        self.llm_engine = get_llm_engine()
        self.enabled = self.config.enabled

        if self.enabled:
            logger.info("🤝 Agent Engine initialized")
        else:
            logger.info("ℹ️  Agent Engine disabled in settings")

    async def plan(self, task: str, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Create a plan for completing a task.

        Args:
            task: Task description
            context: Optional context information

        Returns:
            List of planned steps
        """
        if not self.enabled:
            logger.warning("⚠️  Agent Engine is disabled")
            return []

        try:
            logger.info(f"📋 Planning task: {task[:100]}...")

            planning_prompt = f"""You are a planning agent. Break down the following task into clear, executable steps.

Task: {task}

{f'Context: {context}' if context else ''}

Return your plan as a JSON list of steps. Each step should have:
- "action": what to do
- "tool": which tool to use (if applicable)
- "reasoning": why this step is needed

Format:
```json
[
  {{"action": "...", "tool": "...", "reasoning": "..."}},
  ...
]
```

Plan:"""

            # Generate plan using LLM
            plan_text = ""
            async for chunk in self.llm_engine.generate(planning_prompt, stream=True):
                plan_text += chunk

            # Extract JSON from response
            plan = self._extract_json_from_text(plan_text)

            if isinstance(plan, list):
                logger.info(f"✅ Plan created with {len(plan)} steps")
                return plan
            else:
                logger.warning("⚠️  Invalid plan format, returning empty plan")
                return []

        except Exception as e:
            logger.error(f"❌ Error creating plan: {e}")
            return []

    async def execute_plan(
        self,
        plan: List[Dict[str, Any]],
        tools: Dict[str, Callable],
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute a plan using available tools.

        Args:
            plan: List of steps to execute
            tools: Dictionary of available tools {name: function}
            callback: Optional callback for progress updates

        Returns:
            Execution results
        """
        if not self.enabled:
            logger.warning("⚠️  Agent Engine is disabled")
            return {"success": False, "error": "Agent Engine disabled"}

        try:
            logger.info(f"🚀 Executing plan with {len(plan)} steps...")

            results = []
            context = ""

            for i, step in enumerate(plan, 1):
                action = step.get('action', '')
                tool_name = step.get('tool', None)
                reasoning = step.get('reasoning', '')

                logger.info(f"Step {i}/{len(plan)}: {action}")

                if callback:
                    await callback({
                        "type": "step_start",
                        "step": i,
                        "total": len(plan),
                        "action": action,
                        "reasoning": reasoning
                    })

                # Execute step
                if tool_name and tool_name in tools:
                    # Use tool
                    try:
                        tool_func = tools[tool_name]
                        result = await tool_func(action, context)
                        results.append({
                            "step": i,
                            "action": action,
                            "tool": tool_name,
                            "result": result,
                            "success": True
                        })
                        context += f"\nStep {i} result: {result}"
                        logger.info(f"✅ Step {i} completed using {tool_name}")
                    except Exception as e:
                        logger.error(f"❌ Step {i} failed: {e}")
                        results.append({
                            "step": i,
                            "action": action,
                            "tool": tool_name,
                            "error": str(e),
                            "success": False
                        })
                else:
                    # Execute with LLM
                    try:
                        step_result = ""
                        async for chunk in self.llm_engine.generate(
                            f"{action}\n\nContext: {context}",
                            stream=True
                        ):
                            step_result += chunk

                        results.append({
                            "step": i,
                            "action": action,
                            "result": step_result,
                            "success": True
                        })
                        context += f"\nStep {i} result: {step_result}"
                        logger.info(f"✅ Step {i} completed with LLM")
                    except Exception as e:
                        logger.error(f"❌ Step {i} failed: {e}")
                        results.append({
                            "step": i,
                            "action": action,
                            "error": str(e),
                            "success": False
                        })

                if callback:
                    await callback({
                        "type": "step_complete",
                        "step": i,
                        "result": results[-1]
                    })

            logger.info("✅ Plan execution completed")

            return {
                "success": True,
                "results": results,
                "total_steps": len(plan),
                "completed_steps": sum(1 for r in results if r.get('success', False))
            }

        except Exception as e:
            logger.error(f"❌ Error executing plan: {e}")
            return {"success": False, "error": str(e)}

    async def reflect(self, task: str, results: Dict[str, Any]) -> str:
        """
        Reflect on execution results and provide analysis.

        Args:
            task: Original task
            results: Execution results

        Returns:
            Reflection text
        """
        try:
            reflection_prompt = f"""Analyze the following task execution and provide insights.

Task: {task}

Results: {json.dumps(results, indent=2)}

Provide:
1. Summary of what was accomplished
2. Quality assessment
3. Potential improvements
4. Any issues encountered

Reflection:"""

            reflection = ""
            async for chunk in self.llm_engine.generate(reflection_prompt, stream=True):
                reflection += chunk

            logger.info("🤔 Reflection completed")
            return reflection

        except Exception as e:
            logger.error(f"❌ Error during reflection: {e}")
            return f"Error during reflection: {str(e)}"

    async def react_loop(
        self,
        task: str,
        tools: Dict[str, Callable],
        max_iterations: Optional[int] = None,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute ReAct (Reasoning + Acting) loop.

        Args:
            task: Task to complete
            tools: Available tools
            max_iterations: Maximum iterations (default: config.max_iterations)
            callback: Progress callback

        Returns:
            Final result
        """
        if not self.enabled:
            return {"success": False, "error": "Agent Engine disabled"}

        try:
            max_iterations = max_iterations or self.config.max_iterations
            logger.info(f"🔄 Starting ReAct loop (max {max_iterations} iterations)...")

            context = f"Task: {task}\n\nAvailable tools: {', '.join(tools.keys())}\n"
            iterations = []

            for iteration in range(max_iterations):
                logger.info(f"Iteration {iteration + 1}/{max_iterations}")

                # Thought: What should I do next?
                thought_prompt = f"""{context}

What should I do next to complete the task?

Think step by step:
1. What have I accomplished so far?
2. What still needs to be done?
3. Which tool (if any) should I use next?
4. Am I done?

Respond in this format:
Thought: [your reasoning]
Action: [tool name or "FINISH"]
Action Input: [input for the tool]

Response:"""

                response = ""
                async for chunk in self.llm_engine.generate(thought_prompt, stream=False):
                    response += chunk

                # Parse response
                thought, action, action_input = self._parse_react_response(response)

                iteration_data = {
                    "iteration": iteration + 1,
                    "thought": thought,
                    "action": action,
                    "action_input": action_input
                }

                if callback:
                    await callback({"type": "iteration", "data": iteration_data})

                # Check if done
                if action.upper() == "FINISH":
                    logger.info("✅ Agent decided to finish")
                    iteration_data["observation"] = "Task completed"
                    iterations.append(iteration_data)
                    break

                # Execute action
                if action in tools:
                    try:
                        observation = await tools[action](action_input)
                        iteration_data["observation"] = observation
                        context += f"\nObservation: {observation}\n"
                        logger.info(f"✅ Action '{action}' executed")
                    except Exception as e:
                        observation = f"Error: {str(e)}"
                        iteration_data["observation"] = observation
                        context += f"\nObservation (error): {observation}\n"
                        logger.error(f"❌ Action '{action}' failed: {e}")
                else:
                    observation = f"Tool '{action}' not found"
                    iteration_data["observation"] = observation
                    context += f"\nObservation: {observation}\n"
                    logger.warning(f"⚠️  Unknown action: {action}")

                iterations.append(iteration_data)

            return {
                "success": True,
                "iterations": iterations,
                "total_iterations": len(iterations)
            }

        except Exception as e:
            logger.error(f"❌ Error in ReAct loop: {e}")
            return {"success": False, "error": str(e)}

    def _extract_json_from_text(self, text: str) -> Any:
        """Extract JSON from text (handles markdown code blocks)"""
        try:
            # Try to find JSON in code blocks
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                json_text = text[start:end].strip()
            elif "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                json_text = text[start:end].strip()
            else:
                json_text = text.strip()

            return json.loads(json_text)
        except Exception as e:
            logger.error(f"❌ Error parsing JSON: {e}")
            return None

    def _parse_react_response(self, response: str) -> tuple:
        """Parse ReAct response format"""
        thought = ""
        action = "FINISH"
        action_input = ""

        try:
            lines = response.split('\n')
            for line in lines:
                if line.startswith("Thought:"):
                    thought = line.replace("Thought:", "").strip()
                elif line.startswith("Action:"):
                    action = line.replace("Action:", "").strip()
                elif line.startswith("Action Input:"):
                    action_input = line.replace("Action Input:", "").strip()

        except Exception as e:
            logger.error(f"❌ Error parsing ReAct response: {e}")

        return thought, action, action_input


# Singleton instance
_agent_engine_instance = None


def get_agent_engine() -> AgentEngine:
    """Get or create Agent Engine singleton"""
    global _agent_engine_instance
    if _agent_engine_instance is None:
        _agent_engine_instance = AgentEngine()
    return _agent_engine_instance


# Export
__all__ = ['AgentEngine', 'get_agent_engine']
