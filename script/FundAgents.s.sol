// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "forge-std/Test.sol"; // 1. Add this import
import "../src/IMNEE.sol";

// 2. Inherit from BOTH Script and Test
contract FundAgents is Script, Test {
    address constant MNEE_ADDR = 0xf7461a489c71EAE6fA1Bfe69F8c3d661De0619Da;

    // Default Anvil Accounts
    address constant ALICE_WORKER = 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266;
    address constant BOB_EMPLOYER = 0x70997970C51812dc3A010C7d01b50e0d17dc79C8;

    function run() external {
        // Start "God Mode"
        vm.startBroadcast();

        // Now 'deal' will work because we inherited 'Test'
        deal(MNEE_ADDR, ALICE_WORKER, 10_000 * 1e18);
        deal(MNEE_ADDR, BOB_EMPLOYER, 10_000 * 1e18);

        vm.stopBroadcast();

        console.log("--- Funding Complete ---");
        // We use the interface to check balances
        console.log("Alice Balance:", IMNEE(MNEE_ADDR).balanceOf(ALICE_WORKER));
        console.log("Bob Balance:", IMNEE(MNEE_ADDR).balanceOf(BOB_EMPLOYER));
    }
}