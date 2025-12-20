// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/AgentRegistry.sol";

interface IMNEE is IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract StakingTest is Test {
    AgentRegistry registry;
    address constant MNEE_ADDR = 0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF;
    
    address agent = address(0x777);
    address admin = address(this); 

    function setUp() public {
        string memory rpc = vm.envOr("RPC_URL", string(""));
        vm.createSelectFork(rpc);

        registry = new AgentRegistry(MNEE_ADDR);
    }

    function testStakingFlow() public {
        uint256 stake = 50 * 10**18;
        
        // 1. Give Agent MNEE
        deal(MNEE_ADDR, agent, stake);

        // 2. Approve Registry
        vm.startPrank(agent);
        IMNEE(MNEE_ADDR).approve(address(registry), stake);
        
        // 3. Register
        registry.registerAgent("DATA_ANALYSIS", 100e18);
        vm.stopPrank();

        // CHECK: Registry took the money
        assertEq(IMNEE(MNEE_ADDR).balanceOf(address(registry)), stake, "Stake not locked");
        
        // 4. Slash Agent
        registry.slashAgent(agent);

        // CHECK: Agent deactivated
        AgentRegistry.AgentProfile memory profile = registry.getAgentDetails(agent);
        assertEq(profile.isActive, false, "Agent was not banned");
        assertEq(profile.isStaked, false, "Stake flag not cleared");

        console.log("--- Day 6 COMPLETE: Staking & Slashing Works ---");
    }

    // FIXED: Modern way to test for failure
    function testNoMoney_Revert() public {
        address brokeAgent = address(0x999);
        vm.prank(brokeAgent);
        
        // We explicitly tell Foundry: "The next line MUST fail"
        vm.expectRevert(); 
        registry.registerAgent("SCAMMER", 100e18);
    }
}