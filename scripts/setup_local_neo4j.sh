#!/bin/bash
# Setup Local Neo4j with Docker
# Quick development environment

echo "🐳 Setting up local Neo4j with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Stop and remove existing container if any
echo "🧹 Cleaning up existing Neo4j container..."
docker stop neo4j-helixgraph 2>/dev/null
docker rm neo4j-helixgraph 2>/dev/null

# Start Neo4j container
echo "🚀 Starting Neo4j container..."
docker run -d \
    --name neo4j-helixgraph \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/helixgraph123 \
    -e NEO4J_PLUGINS='["apoc"]' \
    -v ~/neo4j/data:/data \
    neo4j:latest

# Wait for Neo4j to start
echo "⏳ Waiting for Neo4j to start (30 seconds)..."
sleep 30

# Check status
if docker ps | grep -q neo4j-helixgraph; then
    echo ""
    echo "✅ Neo4j is running!"
    echo ""
    echo "📋 Connection Info:"
    echo "   URI: bolt://localhost:7687"
    echo "   Username: neo4j"
    echo "   Password: helixgraph123"
    echo "   Browser: http://localhost:7474"
    echo ""
    echo "🔧 Update your .env file:"
    echo "   NEO4J_URI=bolt://localhost:7687"
    echo "   NEO4J_USERNAME=neo4j"
    echo "   NEO4J_PASSWORD=helixgraph123"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Update .env with local credentials"
    echo "   2. Run: python scripts/import_data_to_neo4j.py"
    echo "   3. Import will complete in 30 seconds!"
else
    echo "❌ Failed to start Neo4j"
    docker logs neo4j-helixgraph
fi
