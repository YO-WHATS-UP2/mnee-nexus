// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/TaskEscrow.sol";

interface IMNEE is IERC20 {
    function balanceOf(address) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function decimals() external view returns (uint8);
}

contract EscrowTest is Test {
    TaskEscrow public escrow;
    address constant MNEE_ADDR = 0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF;
    IMNEE mnee = IMNEE(MNEE_ADDR);

    address constant EMPLOYER = address(0xABC); 
    address constant WORKER = address(0x123);   

    function setUp() public {
        // SAFE: This reads from your hidden .env file
        string memory rpc = vm.envOr("RPC_URL", string(""));
        vm.createSelectFork(rpc);

        escrow = new TaskEscrow(MNEE_ADDR);
    }
    function testEscrowFlow() public {
        uint256 payAmount = 100 * 10**18; 

        // 1. Fund the Employer
        deal(MNEE_ADDR, EMPLOYER, payAmount);

        // 2. Employer hires Worker
        vm.startPrank(EMPLOYER);
        mnee.approve(address(escrow), payAmount);
        uint256 taskId = escrow.createTask(WORKER, payAmount);
        vm.stopPrank();

        console.log("Task Created ID:", taskId);

        // Verify Vault has the money
        assertEq(mnee.balanceOf(address(escrow)), payAmount, "Vault did not receive MNEE");

        // 3. Worker completes the job
        vm.prank(WORKER);
        escrow.completeTask(taskId);

        // 4. Release Funds
        escrow.releaseFunds(taskId);

        // Verify Worker got paid
        assertEq(mnee.balanceOf(WORKER), payAmount, "Worker did not get paid");
        assertEq(mnee.balanceOf(address(escrow)), 0, "Vault is not empty");
        
        console.log("--- Day 4 COMPLETE: Money Moved Successfully ---");
    }
}