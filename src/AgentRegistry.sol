// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./IMNEE.sol"; // Import the shared file

contract AgentRegistry {
    IMNEE public immutable MNEE_TOKEN; // Use IMNEE instead of IERC20
    address public admin;

    uint256 public constant STAKE_AMOUNT = 50 * 10**18;

    struct AgentProfile {
        address wallet;       
        string serviceTag;    
        uint256 hourlyRate;   
        uint256 reputation;   
        bool isActive;
        bool isStaked;
    }

    mapping(address => AgentProfile) public agents;
    mapping(string => address[]) public serviceProviders;

    event AgentRegistered(address indexed agent, string service, uint256 rate);
    event AgentSlashed(address indexed agent);

    constructor(address _mneeToken) {
        MNEE_TOKEN = IMNEE(_mneeToken);
        admin = msg.sender;
    }

    function registerAgent(string memory _serviceTag, uint256 _hourlyRate) external {
        require(bytes(_serviceTag).length > 0, "Service tag required");
        require(_hourlyRate > 0, "Rate must be > 0");
        require(!agents[msg.sender].isStaked, "Already registered");

        bool success = MNEE_TOKEN.transferFrom(msg.sender, address(this), STAKE_AMOUNT);
        require(success, "Stake transfer failed");

        if (agents[msg.sender].wallet == address(0)) {
            serviceProviders[_serviceTag].push(msg.sender);
        }

        agents[msg.sender] = AgentProfile({
            wallet: msg.sender,
            serviceTag: _serviceTag,
            hourlyRate: _hourlyRate,
            reputation: 1,
            isActive: true,
            isStaked: true
        });

        emit AgentRegistered(msg.sender, _serviceTag, _hourlyRate);
    }

    function slashAgent(address _agent) external {
        require(msg.sender == admin, "Only admin");
        require(agents[_agent].isStaked, "Not staked");

        agents[_agent].isActive = false;
        agents[_agent].isStaked = false;
        emit AgentSlashed(_agent);
    }

    function getAgentsByService(string memory _serviceTag) external view returns (address[] memory) {
        return serviceProviders[_serviceTag];
    }
    
    function getAgentDetails(address _agent) external view returns (AgentProfile memory) {
        return agents[_agent];
    }
}