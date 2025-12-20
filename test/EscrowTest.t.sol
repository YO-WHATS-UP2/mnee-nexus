// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/TaskEscrow.sol";
import "../src/IMNEE.sol"; // Import the real interface

contract EscrowTest is Test {
    TaskEscrow public escrow;
    address constant MNEE_ADDR = 0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF;
    
    // Use the real interface
    IMNEE mnee = IMNEE(MNEE_ADDR);

    address constant EMPLOYER = address(0xABC); 
    address constant WORKER = address(0x123);   

    function setUp() public {
        string memory rpc = vm.envOr("RPC_URL", string(""));
        vm.createSelectFork(rpc);

        escrow = new TaskEscrow(MNEE_ADDR);
    }

    function testEscrowFlow() public {
        uint256 payAmount = 100 * 10**18; 

        deal(MNEE_ADDR, EMPLOYER, payAmount);

        vm.startPrank(EMPLOYER);
        mnee.approve(address(escrow), payAmount);
        uint256 taskId = escrow.createTask(WORKER, payAmount);
        vm.stopPrank();

        // Worker completes
        vm.prank(WORKER);
        escrow.completeTask(taskId);

        // Time Travel
        vm.warp(block.timestamp + 1 days + 1 seconds);

        // Withdraw
        escrow.withdraw(taskId);

        assertEq(mnee.balanceOf(WORKER), payAmount, "Worker did not get paid");
        assertEq(mnee.balanceOf(address(escrow)), 0, "Vault is not empty");
    }
}