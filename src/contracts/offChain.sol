pragma solidity >=0.4.21 <0.6.0;

import "./common/SafeMath.sol";
import "./common/Ownable.sol";
import "./common/Destructible.sol";


contract offChain is Ownable, Destructible {

    using SafeMath for uint256;
    address public owner;
    uint public balance;
    mapping (string => address) private eventHashes;

    event Balance(uint amount, uint moneyNeeded);
    event QueryRes(string result);

    constructor() public {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function _addEvent(string memory hash) public {
        eventHashes[hash] = msg.sender;
    }

    function _verifyEvent(string eventInfo) public view returns(bool) {
        string hash = sha256(abi.encodePacked(eventInfo));
        if (eventHashes[x].exists == true) {
            return true;
        } else {
            return false;
        }
    }

    function _retrieveCreator(string eventInfo) public view returns(address) {
        return eventHashes[x];
    }
}