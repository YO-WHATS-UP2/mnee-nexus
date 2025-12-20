// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/AgentRegistry.sol";

contract RegistryTest is Test {
    AgentRegistry public registry;
    // We need the MNEE address now
    address constant MNEE_ADDR = 0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF;

    address constant PYTHON_BOT = address(0x111);
    address constant ART_BOT = address(0x222);

    function setUp() public {
        // Safe Env Load
        string memory rpc = vm.envOr("RPC_URL", string(""));
        vm.createSelectFork(rpc);

        // FIX: Pass the MNEE Address to the constructor
        registry = new AgentRegistry(MNEE_ADDR);
    }

    function testRegistration() public {
        // We need to give the bot money and approve it first (Day 6 Logic)
        uint256 stake = 50 * 1e18;
        deal(MNEE_ADDR, PYTHON_BOT, stake);

        vm.startPrank(PYTHON_BOT);
        
        // Approve the registry to take the stake
        // (We use a low-level call here to avoid importing the whole interface in this simple test)
        (bool success, ) = MNEE_ADDR.call(abi.encodeWithSignature("approve(address,uint256)", address(registry), stake));
        require(success, "Approve failed");

        // Register
        uint256 rate = 50 * 1e18; 
        registry.registerAgent("PYTHON", rate);
        
        vm.stopPrank();

        AgentRegistry.AgentProfile memory profile = registry.getAgentDetails(PYTHON_BOT);
        assertEq(profile.serviceTag, "PYTHON");
    }

    function testDiscovery() public {
        // Setup Python Bot
        uint256 stake = 50 * 1e18;
        deal(MNEE_ADDR, PYTHON_BOT, stake);
        vm.startPrank(PYTHON_BOT);
        MNEE_ADDR.call(abi.encodeWithSignature("approve(address,uint256)", address(registry), stake));
        registry.registerAgent("PYTHON", 50e18);
        vm.stopPrank();

        // Search
        address[] memory foundAgents = registry.getAgentsByService("PYTHON");
        assertEq(foundAgents.length, 1);
        assertEq(foundAgents[0], PYTHON_BOT);
    }
}