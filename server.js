/*
TODO: send email if temp goes above/below certain value


*/



var mongoose   = require('mongoose'),
    express    = require('express'),
    config     = require('./config/database'),
    actions    = require('./actions/methods'),
    bodyParser = require('body-parser');



mongoose.connect(config.database); // connect to __________

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

router.get('/get_total', actions.get_add_datapoints_from_DB);

router.post('/add_data', actions.add_data);




// remove the powered by express message, because you know.. hackrz
app.use(function (req, res, next) {
  res.setHeader("x-powered-by", "An appropriately compensated, yet overly worked, hamster");  // mmmmm
  next();
});


app.use('/', router);   // base router URL

app.listen(port);
console.log('And we\'re rolling: on port ' + port);
