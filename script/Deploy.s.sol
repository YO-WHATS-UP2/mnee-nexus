// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/AgentRegistry.sol";
import "../src/TaskEscrow.sol";

contract DeploySwarm is Script {
    // Official MNEE Address
    address constant MNEE_ADDR = 0xf7461a489c71EAE6fA1Bfe69F8c3d661De0619Da;

    function run() external {
        // We use the default Anvil Private Key (Test Money)
        // This corresponds to address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
        uint256 deployerPrivateKey = 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80;

        vm.startBroadcast(deployerPrivateKey);

        console.log("--- Deploying MNEE Swarm Protocol ---");

        // 1. Deploy Registry
        AgentRegistry registry = new AgentRegistry(MNEE_ADDR);
        console.log("AgentRegistry deployed at:", address(registry));

        // 2. Deploy Escrow
        TaskEscrow escrow = new TaskEscrow(MNEE_ADDR);
        console.log("TaskEscrow deployed at:", address(escrow));

        vm.stopBroadcast();
    }
}