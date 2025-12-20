// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// Minimal interface to tell Foundry what MNEE looks like
interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function decimals() external view returns (uint8);
}

contract MNEETest is Test {
    // The Official MNEE Contract Address (Eth Mainnet)
    address constant MNEE_ADDR = 0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF;
    
    IERC20 mnee = IERC20(MNEE_ADDR);

    function setUp() public {
        // Connect to Mainnet using your dRPC (or any public RPC)
        // We use envOr to prevent crashes if the variable isn't set perfectly
        string memory rpc = vm.envOr("RPC_URL", string("https://eth.llamarpc.com"));
        vm.createSelectFork(rpc);
    }

    function testGodMode() public {
        // 1. Get the decimals (should be 18)
        uint8 decimals = mnee.decimals();
        console.log("MNEE Decimals:", decimals);

        // 2. THE GOD MODE TRICK
        // We use 'deal' to write 50,000 MNEE directly into our wallet
        // This works even if the liquidity pool is empty!
        uint256 amount = 50000 * 10**decimals;
        deal(MNEE_ADDR, address(this), amount);

        // 3. Verify it worked
        uint256 myBalance = mnee.balanceOf(address(this));
        console.log("My Balance:", myBalance / 10**decimals, "MNEE");

        // 4. The Final Check
        assertEq(myBalance, amount, "Deal failed to write balance");
        console.log("--- Day 2 COMPLETE: Environment is Ready ---");
    }
}