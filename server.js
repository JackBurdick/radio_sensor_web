var express = require('express'),
    bodyParser = require('body-parser');



var app = express();

var router = express.Router();    //express router

// Server information
var port = process.env.PORT || 3000;

//  Use body parser for json data
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());




// main landing page
router.get('/', function(req, res) {
  //res.send("hi");
  res.json({ message: 'It seems you have reached this page by mistake, nothing to see here' });
});






// remove the powered by express message, because you know.. hackrz
app.use(function (req, res, next) {
  res.setHeader("x-powered-by", "An appropriately compensated, yet overly worked, hamster");  // mmmmm
  next();
});


app.use('/', router);   // base router URL

app.listen(port);
console.log('And we\'re rolling: on port ' + port);
