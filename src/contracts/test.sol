pragma solidity >=0.4.21 <0.6.0;

contract test{

    string public t;

    constructor() public {
        t = "hi";
    }

    function test() view public returns (string memory) {
        return t;
    }
}