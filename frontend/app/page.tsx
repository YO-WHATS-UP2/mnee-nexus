"use client";
import { useState, useEffect, useRef } from "react";
import { ethers } from "ethers";
import SwarmGraph from "./components/SwarmGraph";

// ------------------------------------------------------
// ⚡ CONFIGURATION
// ------------------------------------------------------
const MNEE_TOKEN_ADDR = "0x610178dA211FEF7D417bC0e6FeD39F05609AD788"; 
const ESCROW_ADDR     = "0xa82fF9aFd8f496c3d6ac40E2a0F282E47488CFc9"; // Make sure this matches Python!

// ------------------------------------------------------
// 📜 ABIS
// ------------------------------------------------------
const ERC20_ABI = [
  "function approve(address spender, uint256 amount) public returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)"
];
const ESCROW_ABI = [
  "function createTask(address worker, uint256 amount) external returns (uint256)",
  "event TaskCompleted(uint256 indexed taskId, string output)" // <--- We listen for this!
];

// ------------------------------------------------------
// 🧠 COMPONENT LOGIC
// ------------------------------------------------------
interface Agent { id: string; group: number; color: string; role: string; address?: string; x?: number; y?: number; z?: number; }

export default function Home() {
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [isHiring, setIsHiring] = useState(false);
  const providerRef = useRef<any>(null);

  // MAPPING: Frontend IDs to Real Anvil Addresses
  const AGENT_ADDRESSES: {[key: string]: string} = {
    "Dave": "0x90F79bf6EB2c4f870365E785982E1f101E93b906", 
    "Alice": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266", 
    "Carol": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"  
  };

  const addLog = (msg: string) => setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev]);

  // SETUP LISTENER ON MOUNT
  useEffect(() => {
    addLog("System Online. Link established.");
    
    const setupListener = async () => {
        if (!(window as any).ethereum) return;
        const provider = new ethers.BrowserProvider((window as any).ethereum);
        const escrowContract = new ethers.Contract(ESCROW_ADDR, ESCROW_ABI, provider);

        // Listen for ANY TaskCompleted event
        escrowContract.on("TaskCompleted", (taskId, output) => {
            console.log("EVENT RECEIVED:", taskId, output);
            addLog(`📨 INCOMING TRANSMISSION (Task #${taskId}):`);
            addLog(`> "${output}"`);
        });

        providerRef.current = provider; // Keep reference
    };

    setupListener();

    // Cleanup listener when page closes
    return () => {
        if(providerRef.current) {
            providerRef.current.removeAllListeners();
        }
    };
  }, []);

  // 🧨 THE TRIGGER FUNCTION
  const handleHire = async () => {
    // 1. SAFETY CHECK: Stop immediately if nobody is selected
    if (!selectedAgent) {
        addLog("❌ Error: No agent selected.");
        return;
    }

    // Now it is safe to access .id because we know selectedAgent exists
    const rawId = selectedAgent.id; 
    const agentId = rawId.charAt(0).toUpperCase() + rawId.slice(1);
    
    // 2. ADDRESS CHECK
    if (!AGENT_ADDRESSES[agentId]) {
         addLog(`❌ Error: Address for '${agentId}' not found in registry.`);
         return;
    }

    setIsHiring(true);
    addLog(`INITIATING CONTRACT FOR ${agentId.toUpperCase()}...`);

    try {
      if (!(window as any).ethereum) throw new Error("No Wallet Found");
      const provider = new ethers.BrowserProvider((window as any).ethereum);
      const signer = await provider.getSigner();

      const mneeContract = new ethers.Contract(MNEE_TOKEN_ADDR, ERC20_ABI, signer);
      const escrowContract = new ethers.Contract(ESCROW_ADDR, ESCROW_ABI, signer);
      
      const wage = ethers.parseEther("10"); 
      const workerAddr = AGENT_ADDRESSES[agentId];

      addLog("Step 1/2: Requesting MNEE Approval...");
      const tx1 = await mneeContract.approve(ESCROW_ADDR, wage);
      await tx1.wait();
      addLog("✅ Approval Granted.");

      addLog("Step 2/2: Depositing to Escrow...");
      const tx2 = await escrowContract.createTask(workerAddr, wage);
      await tx2.wait();
      
      addLog(`🚀 SUCCESS! Signal Sent. Waiting for response...`);

    } catch (err: any) {
      console.error(err);
      addLog(`❌ ERROR: ${err.message || "Transaction Failed"}`);
    } finally {
      setIsHiring(false);
    }
  };

  return (
    <main style={{ padding: "2rem", fontFamily: "'Space Mono', monospace", background: "#050505", color: "#e0e0e0", height: "100vh", overflow: "hidden", display: "flex", flexDirection: "column", backgroundImage: "linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px)", backgroundSize: "30px 30px" }}>
      <style jsx global>{` @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap'); ::-webkit-scrollbar { width: 8px; } ::-webkit-scrollbar-track { background: #111; } ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; } `}</style>
      
      {/* HEADER */}
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem", flexShrink: 0, borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
          <div style={{ fontSize: "2rem" }}>🐝</div>
          <div>
            <h1 style={{ fontSize: "1.8rem", margin: 0, letterSpacing: "-1px", lineHeight: "1" }}>MNEE <span style={{color: "#bf00ff", textShadow: "0 0 20px #bf00ff"}}>NEXUS</span></h1>
            <span style={{ fontSize: "0.7rem", color: "#666", letterSpacing: "2px" }}>AUTONOMOUS AGENT SWARM</span>
          </div>
        </div>
        <div style={{ color: "#0f0", fontSize: "0.9rem", display: "flex", alignItems: "center", gap: "6px" }}>
          <span style={{ width: "8px", height: "8px", background: "#0f0", borderRadius: "50%", boxShadow: "0 0 8px #0f0" }}></span> OPERATIONAL
        </div>
      </header>
      
      {/* CONTENT */}
      <div style={{ display: "flex", gap: "25px", flex: 1, minHeight: 0 }}>
        {/* GRAPH */}
        <div style={{ flex: 3, position: "relative", minWidth: 0, display: "flex", flexDirection: "column", border: "1px solid rgba(0, 243, 255, 0.2)", borderRadius: "12px", overflow: "hidden", boxShadow: "0 0 30px rgba(0,0,0,0.5)" }}>
           <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, background: "linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06))", zIndex: 10, pointerEvents: "none", backgroundSize: "100% 2px, 3px 100%" }}></div>
           <SwarmGraph onNodeClick={setSelectedAgent} />
        </div>

        {/* SIDEBAR */}
        <div style={{ flex: 1, minWidth: "320px", maxWidth: "420px", display: "flex", flexDirection: "column", gap: "20px" }}>
          
          {/* CONTROLS */}
          <div style={{ background: "rgba(20, 20, 20, 0.6)", backdropFilter: "blur(10px)", border: "1px solid rgba(255, 255, 255, 0.1)", borderRadius: "12px", padding: "25px", flex: 1, display: "flex", flexDirection: "column", boxShadow: "0 10px 30px rgba(0,0,0,0.3)" }}>
            <h3 style={{ borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: "15px", margin: "0 0 20px 0", color: "#888", fontSize: "0.75rem", letterSpacing: "2px", display: "flex", justifyContent: "space-between" }}>
              <span>TARGET COMMAND</span>
              {selectedAgent && <span style={{color: selectedAgent.color}}>● LOCKED</span>}
            </h3>
            
            {selectedAgent ? (
              <div style={{ animation: "fadeIn 0.3s ease-in" }}>
                <h2 style={{ color: selectedAgent.color, fontSize: "2.5rem", margin: 0, lineHeight: 1 }}>{selectedAgent.id.toUpperCase()}</h2>
                <div style={{ background: selectedAgent.color, color: "#000", padding: "2px 8px", fontSize: "0.6rem", fontWeight: "bold", borderRadius: "2px", display: "inline-block", marginTop: "4px" }}>{selectedAgent.role}</div>
                
                <button 
                  disabled={isHiring}
                  onClick={handleHire}
                  style={{ marginTop: "25px", width: "100%", padding: "14px", background: isHiring ? "#333" : `linear-gradient(45deg, ${selectedAgent.color}22, transparent)`, border: `1px solid ${selectedAgent.color}`, color: isHiring ? "#888" : selectedAgent.color, cursor: isHiring ? "wait" : "pointer", fontFamily: "inherit", fontWeight: "bold", fontSize: "0.8rem", letterSpacing: "1px", transition: "all 0.2s", boxShadow: `0 0 15px ${selectedAgent.color}22` }} 
                >
                  {isHiring ? "[ TRANSMITTING... ]" : `[ DEPLOY ${selectedAgent.id.toUpperCase()} ]`}
                </button>
              </div>
            ) : (
              <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "#444", border: "1px dashed rgba(255,255,255,0.1)", borderRadius: "8px", flexDirection: "column", gap: "10px" }}>
                <div style={{ fontSize: "2rem", opacity: 0.5 }}>⌖</div><div>AWAITING SELECTION</div>
              </div>
            )}
          </div>

          {/* LOGS */}
          <div style={{ background: "#080808", border: "1px solid rgba(255,255,255,0.1)", padding: "15px", borderRadius: "12px", height: "250px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "6px", fontFamily: "monospace", fontSize: "0.75rem", boxShadow: "inset 0 0 20px rgba(0,0,0,0.8)" }}>
            {logs.map((log, i) => <div key={i} style={{ color: i === 0 ? "#fff" : "#666" }}>{log}</div>)}
          </div>

        </div>
      </div>
    </main>
  );
}