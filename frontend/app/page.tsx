"use client";
import { useState, useEffect, useRef } from "react";
import { ethers } from "ethers";
import SwarmGraph from "./components/SwarmGraph";

// ------------------------------------------------------
// ⚡ CONFIGURATION
// ------------------------------------------------------
const MNEE_TOKEN_ADDR = "0x4030B20dCFBF4Dd4EE040F2cFC7B773c7e3344Fa"; 
const ESCROW_ADDR     = "0xab9270a58bEAC035245059fC7f686DE63e67bC73";

// ------------------------------------------------------
// 📜 ABIS
// ------------------------------------------------------
const ERC20_ABI = [
  "function approve(address spender, uint256 amount) public returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)"
];
const ESCROW_ABI = [
  "function createTask(address worker, uint256 amount) external returns (uint256)",
  "event TaskCompleted(uint256 indexed taskId, string output)" 
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

  // MAPPING: Frontend IDs to Real Sepolia Addresses
  const AGENT_ADDRESSES: {[key: string]: string} = {
    "Dave":  "0x3F5643702798166FD76F928249C0e022963025E1", 
    "Alice": "0x3F5643702798166FD76F928249C0e022963025E1", 
    "Carol": "0x3F5643702798166FD76F928249C0e022963025E1"  
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
            // We pass the raw output here so the detector can find the link
            addLog(`${output}`); 
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
    if (!selectedAgent) {
        addLog("❌ Error: No agent selected.");
        return;
    }

    const rawId = selectedAgent.id; 
    const agentId = rawId.charAt(0).toUpperCase() + rawId.slice(1);
    
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
      let wageAmount = "10"; // Default (Alice)
      if (agentId === "Carol") wageAmount = "11";
      if (agentId === "Dave")  wageAmount = "12";
      const wage = ethers.parseEther(wageAmount);
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

          {/* LOGS (UPDATED WITH LINK DETECTOR) */}
          <div style={{ background: "#080808", border: "1px solid rgba(255,255,255,0.1)", padding: "15px", borderRadius: "12px", height: "300px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "10px", fontFamily: "monospace", fontSize: "0.75rem", boxShadow: "inset 0 0 20px rgba(0,0,0,0.8)" }}>
            {logs.map((log, i) => {
                // 🔍 DETECTOR: Check if this log contains an IPFS/HTTP Link
                const hasLink = log.includes("http");
                
                return (
                    <div key={i} style={{ color: i === 0 ? "#fff" : "#888", borderBottom: "1px solid rgba(255,255,255,0.05)", paddingBottom: "8px" }}>
                        {hasLink ? (
                            // 🎨 RENDER IMAGE + LINK
                            <div>
                                <div style={{marginBottom: "5px"}}>{log.split("http")[0]}</div>
                                
                                <a 
                                    href={`http${log.split("http")[1]}`} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    style={{ color: "#00f3ff", textDecoration: "underline", display: "block", marginBottom: "8px", wordBreak: "break-all" }}
                                >
                                    [ VIEW IMAGE ON IPFS ]
                                </a>

                                <div style={{ borderRadius: "8px", overflow: "hidden", border: "1px solid #333", background: "#000" }}>
                                    <img 
                                        src={`http${log.split("http")[1]}`} 
                                        alt="Agent Generated Art" 
                                        style={{ width: "100%", height: "auto", display: "block" }} 
                                    />
                                </div>
                            </div>
                        ) : (
                            // 📄 RENDER NORMAL TEXT
                            log
                        )}
                    </div>
                )
            })}
          </div>

        </div>
      </div>
    </main>
  );
}