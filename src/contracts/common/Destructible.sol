pragma solidity ^0.6.1;

import './Ownable.sol';

contract Destructible is Ownable {

    constructor() public payable { }

    function destroy() public onlyOwner {
        selfdestruct(owner);
    }

    function destroyAndSend(address _recipient) public onlyOwner {
        selfdestruct(_recipient);
    }
}
