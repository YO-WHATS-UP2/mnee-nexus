// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/MNEE.sol";

contract DeployToken is Script {
    function run() external {
        vm.startBroadcast();
        MNEE mnee = new MNEE();
        console.log("NEW_MNEE_ADDRESS:", address(mnee));
        vm.stopBroadcast();
    }
}