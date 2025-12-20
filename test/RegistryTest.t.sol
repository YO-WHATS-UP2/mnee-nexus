// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/AgentRegistry.sol";

contract RegistryTest is Test {
    AgentRegistry public registry;

    // Mock Addresses for our Agents
    address constant PYTHON_BOT = address(0x111);
    address constant ART_BOT = address(0x222);

    function setUp() public {
        registry = new AgentRegistry();
    }

    function testRegistration() public {
        // 1. Pretend to be the Python Bot
        vm.startPrank(PYTHON_BOT);
        
        // Register: "I write Python for 50 MNEE"
        uint256 rate = 50 * 1e18; 
        registry.registerAgent("PYTHON", rate);
        
        vm.stopPrank();

        // 2. Check if the data was saved correctly
        AgentRegistry.AgentProfile memory profile = registry.getAgentDetails(PYTHON_BOT);
        
        console.log("Agent Service:", profile.serviceTag);
        console.log("Agent Rate:", profile.hourlyRate);

        assertEq(profile.serviceTag, "PYTHON");
        assertEq(profile.hourlyRate, rate);
    }

    function testDiscovery() public {
        // Register two different agents
        vm.prank(PYTHON_BOT);
        registry.registerAgent("PYTHON", 50e18);

        vm.prank(ART_BOT);
        registry.registerAgent("DESIGN", 100e18);

        // 3. Search for "PYTHON" agents
        address[] memory foundAgents = registry.getAgentsByService("PYTHON");
        
        console.log("Found Agents Count:", foundAgents.length);
        
        assertEq(foundAgents.length, 1);
        assertEq(foundAgents[0], PYTHON_BOT);
        console.log("--- Day 3 COMPLETE: Registry Logic Works ---");
    }
}