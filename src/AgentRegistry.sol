// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AgentRegistry {
    // 1. Define the Agent "Business Card"
    struct AgentProfile {
        address wallet;       // The agent's payment address
        string serviceTag;    // e.g., "PYTHON_DEV", "TRANSLATOR"
        uint256 hourlyRate;   // Price in MNEE (18 decimals)
        uint256 reputation;   // Simple score (starts at 1)
        bool isActive;        // Is the agent open for work?
    }

    // 2. Database Mappings
    // Map wallet address -> Profile
    mapping(address => AgentProfile) public agents;
    
    // Map service tag -> List of Agent Wallets (for discovery)
    mapping(string => address[]) public serviceProviders;

    // 3. Events (Critical for your Frontend Graph later!)
    event AgentRegistered(address indexed agent, string service, uint256 rate);
    event AgentUpdated(address indexed agent, bool isActive);

    // 4. Registration Function
    function registerAgent(string memory _serviceTag, uint256 _hourlyRate) external {
        require(bytes(_serviceTag).length > 0, "Service tag required");
        require(_hourlyRate > 0, "Rate must be > 0");

        // If this is a new agent, add them to the service list
        if (agents[msg.sender].wallet == address(0)) {
            serviceProviders[_serviceTag].push(msg.sender);
        }

        // Create/Update the profile
        agents[msg.sender] = AgentProfile({
            wallet: msg.sender,
            serviceTag: _serviceTag,
            hourlyRate: _hourlyRate,
            reputation: 1, // Everyone starts with 1 point
            isActive: true
        });

        emit AgentRegistered(msg.sender, _serviceTag, _hourlyRate);
    }

    // 5. Discovery Function (Used by the AI Python SDK later)
    function getAgentsByService(string memory _serviceTag) external view returns (address[] memory) {
        return serviceProviders[_serviceTag];
    }

    // 6. Profile Lookup
    function getAgentDetails(address _agent) external view returns (AgentProfile memory) {
        return agents[_agent];
    }
}