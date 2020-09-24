pragma solidity >=0.4.21 <0.6.0;

import "./common/SafeMath.sol";
import "./common/Ownable.sol";
import "./common/Destructible.sol";
import "./provableAPI_0.5.sol";

contract offChain is usingProvable, Ownable, Destructible {

    constructor() public {

    }
}