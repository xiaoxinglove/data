class MCPRuntime:
    def execute(self, tool: str, args: object) -> dict[str, object]:
        return {"tool": tool, "result": None}
