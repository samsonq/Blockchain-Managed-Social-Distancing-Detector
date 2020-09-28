pragma solidity >=0.4.21 <0.6.0;

import "./common/SafeMath.sol";
import "./common/Ownable.sol";
import "./common/Destructible.sol";


contract offChain is Ownable, Destructible {

    using SafeMath for uint256;
    address public owner;
    uint public balance;
    //string[] memory private event_hashes;
    mapping (string => address) private eventHashes;

    event Balance(uint amount, uint moneyNeeded);
    event QueryRes(string result);

    constructor() public {
        owner = msg.sender;
    }

    function _addEvent(string memory hash) public {
        eventHashes.push(hash);
    }

    function _verifyEvent(string eventInfo) public view returns(bool) {
        string hash = sha256(abi.encodePacked(eventInfo));
        if (eventHashes[x].exists == true) {
            return true;
        } else {
            return false;
        }
    }
}