// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/TaskEscrow.sol";

interface IMNEE is IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
}

contract DisputeTest is Test {
    TaskEscrow escrow;
    address constant MNEE = 0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF;
    
    address employer = address(0x111);
    address worker = address(0x222);

    function setUp() public {
        string memory rpc = vm.envOr("RPC_URL", string(""));
        vm.createSelectFork(rpc);
        
        escrow = new TaskEscrow(MNEE);
        deal(MNEE, employer, 1000e18);
    }

    function testDisputeFlow() public {
        uint256 amount = 100e18;

        // 1. Hire
        vm.startPrank(employer);
        IMNEE(MNEE).approve(address(escrow), amount);
        uint256 taskId = escrow.createTask(worker, amount);
        vm.stopPrank();

        // 2. Work
        vm.prank(worker);
        escrow.completeTask(taskId);

        // 3. Try to withdraw immediately (Should FAIL)
        vm.prank(worker);
        vm.expectRevert("Wait for dispute window");
        escrow.withdraw(taskId);
        console.log("Passed: Worker prevented from early withdraw");

        // 4. Time Travel 25 Hours
        vm.warp(block.timestamp + 25 hours);

        // 5. Withdraw Success
        vm.prank(worker);
        escrow.withdraw(taskId);
        console.log("Passed: Worker withdrew after timeout");
        console.log("--- Day 5 COMPLETE: Judge & Jury Ready ---");
    }
}