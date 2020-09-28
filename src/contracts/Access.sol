pragma solidity >=0.4.21 <0.6.0;

import "./common/SafeMath.sol";
import "./common/Ownable.sol";
import "./common/Destructible.sol";
import "./provableAPI_0.5.sol";

contract Access is usingProvable, Ownable, Destructible {

    using SafeMath for uint256;
    address public owner;
    uint public balance;
    event LogNewProvableQuery(string description);
    event Balance(uint amount, uint moneyNeeded);
    event QueryRes(string result);

    constructor() public {
        owner = msg.sender;
    }

    function __callback(bytes32 myid, string memory result) public {
       if (msg.sender != provable_cbAddress()) revert("Not Enough Funds");
       res = result;
       emit QueryRes(res);
   }

    function() payable external {}

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function queryDB() public payable {
       //emit Balance(address(this).balance, provable_getPrice("URL"));
       if (provable_getPrice("URL") > address(this).balance) {
           emit LogNewProvableQuery("Provable query was NOT sent, please add some ETH to cover for the query fee");
       } else {
           emit LogNewProvableQuery("Provable query was sent, standing by for the answer..");
           provable_query("URL", "json(https://purple-elephant-56.localtunnel.me/1/Danny).name");
       }
   }

    function getRes() public view returns (string memory) {
        return res;
    }
}