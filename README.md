# Stock-Emulator
A stock emulator which lets you create an account that starts with $10,000 and lets you invest in stocks. You can get quotes on stocks, buy stocks, sell stocks, and view your history.

<h2> Usage </h2>
This program runs with Python's Flask microframework. To get started with the app in the command-line type:

    flask run
    
And click on the corresponding link. From here, navigate to the "Register" link in the top right corner and create an account.
Your username and a hash of your password will be stored in a database.
You start out with $10,000.
You may navigate to "Quote" to get quotes on the costs of shares for any particular company, provided you have their trading symbol.
On "Buy" you may type in the trading symbol of the company you wish to buy shares from and the number of shares, and if you have enough money, you will be able to buy those shares.
On "Sell" you may select from the shares you already have and sell shares.
On "History" you may see your transaction history.
On "Deposit" you may add more money to your account by providing a valid credit card number (currently this app only supports VISA, AMEX, or MASTERCARD) and the amount you wish to deposit.
