"use client";
import { useEffect, useState, useRef, useCallback } from 'react';
import dynamic from 'next/dynamic';
import SpriteText from 'three-spritetext';

// Dynamically import ForceGraph3D
const ForceGraph3D = dynamic(() => import('react-force-graph-3d'), { ssr: false });

export default function SwarmGraph({ onNodeClick }) {
  const fgRef = useRef();
  const containerRef = useRef(); // Reference to the wrapper div
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  // 🎨 COLORS
  const COLORS = {
    client: "#00f3ff", 
    agent:  "#bf00ff", 
    auditor:"#ccff00", 
    data:   "#ff9900", 
    ghost:  "#555555", // Made lighter so you can actually see them
    link:   "#ffffff"
  };

  // 1. AUTO-RESIZE LOGIC (The Fix for the Layout)
  useEffect(() => {
    if (!containerRef.current) return;

    const resizeObserver = new ResizeObserver(entries => {
      for (let entry of entries) {
        setDimensions({
          width: entry.contentRect.width,
          height: entry.contentRect.height
        });
      }
    });

    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  // 2. DATA GENERATION
  const [graphData, setGraphData] = useState(() => {
    const mainNodes = [
      { id: 'Bob',    group: 1, val: 60, color: COLORS.client, role: "CLIENT" },
      { id: 'Alice',  group: 2, val: 50, color: COLORS.agent,  role: "CODER" },
      { id: 'Carol',  group: 2, val: 50, color: COLORS.auditor,role: "AUDITOR" },
      { id: 'Dave',   group: 2, val: 50, color: COLORS.data,   role: "ANALYST" },
    ];

    // GHOST DRONES (More of them, closer to center)
    const ghostNodes = Array.from({ length: 50 }).map((_, i) => ({
      id: `Drone_${i}`,
      group: 3,
      val: Math.random() * 15 + 5,
      color: COLORS.ghost,
      role: "IDLE"
    }));

    // Tether them to Bob so they cluster tight
    const links = ghostNodes.map(ghost => ({
      source: 'Bob',
      target: ghost.id,
      color: 'transparent'
    }));

    return { nodes: [...mainNodes, ...ghostNodes], links };
  });

  // 3. FORCE CAMERA ON LOAD
  useEffect(() => {
    setTimeout(() => {
      if (fgRef.current) {
        fgRef.current.cameraPosition({ x: 0, y: 0, z: 280 }, { x: 0, y: 0, z: 0 }, 1000);
      }
    }, 500);
  }, []);

  // 4. SIMULATION
  useEffect(() => {
    setTimeout(() => {
      setGraphData(prev => ({
        ...prev,
        links: [
          ...prev.links,
          { source: 'Bob', target: 'Dave', color: COLORS.link },
          { source: 'Dave', target: 'Carol', color: COLORS.auditor }
        ]
      }));
    }, 1500);
  }, []);

  const handleNodeClick = useCallback(node => {
    if (fgRef.current) {
      const distance = 80;
      const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
      fgRef.current.cameraPosition(
        { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
        node,
        2000
      );
      if(onNodeClick) onNodeClick(node);
    }
  }, [onNodeClick]);

  return (
    <div 
      ref={containerRef} 
      style={{ 
        width: "100%",      // Fill parent width
        height: "100%",     // Fill parent height
        overflow: "hidden", // Cut off anything extra
        borderRadius: "12px", 
        background: "radial-gradient(circle at center, #1a1a1a 0%, #000 100%)",
        boxShadow: "inset 0 0 50px rgba(0,0,0,0.8)" // Inner shadow for depth
      }}
    >
      <ForceGraph3D
        ref={fgRef}
        width={dimensions.width}  // 👈 FORCE EXACT WIDTH
        height={dimensions.height} // 👈 FORCE EXACT HEIGHT
        graphData={graphData}
        backgroundColor="rgba(0,0,0,0)"
        
        nodeLabel="role"
        nodeThreeObject={node => {
          const sprite = new SpriteText(node.id);
          sprite.color = node.color;
          sprite.textHeight = node.group === 3 ? 0 : 8;
          sprite.fontWeight = 'bold';
          sprite.backgroundColor = 'rgba(0,0,0,0.6)';
          sprite.padding = 3;
          sprite.borderRadius = 4;
          return sprite;
        }}
        nodeRelSize={9}
        
        linkColor={link => link.color}
        linkWidth={link => link.color === 'transparent' ? 0 : 2}
        linkDirectionalParticles={link => link.color === 'transparent' ? 0 : 4}
        linkDirectionalParticleSpeed={0.01}
        linkDirectionalParticleWidth={5}
        
        d3VelocityDecay={0.3} // Higher friction stops them drifting apart
        onNodeClick={handleNodeClick}
      />
    </div>
  );
}