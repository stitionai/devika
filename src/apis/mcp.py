from flask import Blueprint, request, jsonify
from src.logger import Logger, route_logger
from src.mcp.server import MCPServer

mcp_bp = Blueprint("mcp", __name__)
logger = Logger()

# Initialize MCP Server
mcp_server = MCPServer()

@mcp_bp.route("/api/mcp", methods=["POST"])
@route_logger(logger)
async def handle_mcp_request():
    """Handle MCP protocol requests"""
    try:
        request_data = request.json
        
        if not request_data:
            return jsonify({
                "error": {
                    "code": -32600,
                    "message": "Invalid Request"
                }
            }), 400
        
        response = await mcp_server.handle_request(request_data)
        
        response_data = {
            "jsonrpc": "2.0",
            "id": response.id
        }
        
        if response.result is not None:
            response_data["result"] = response.result
        
        if response.error is not None:
            response_data["error"] = response.error
            return jsonify(response_data), 400
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"MCP API error: {str(e)}")
        return jsonify({
            "jsonrpc": "2.0",
            "id": request.json.get("id") if request.json else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }), 500

@mcp_bp.route("/api/mcp/tools", methods=["GET"])
@route_logger(logger)
def list_mcp_tools():
    """List available MCP tools"""
    try:
        tools = list(mcp_server.tools.keys())
        return jsonify({
            "tools": tools,
            "count": len(tools)
        })
    except Exception as e:
        logger.error(f"MCP tools list error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcp_bp.route("/api/mcp/capabilities", methods=["GET"])
@route_logger(logger)
def get_mcp_capabilities():
    """Get MCP server capabilities"""
    try:
        capabilities = mcp_server.get_capabilities()
        server_info = mcp_server.get_server_info()
        
        return jsonify({
            "capabilities": capabilities,
            "server_info": server_info
        })
    except Exception as e:
        logger.error(f"MCP capabilities error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcp_bp.route("/api/mcp/health", methods=["GET"])
@route_logger(logger)
def mcp_health_check():
    """MCP server health check"""
    return jsonify({
        "status": "healthy",
        "server": "devika-mcp-server",
        "version": "1.0.0"
    })