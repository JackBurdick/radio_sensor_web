// database
var mongoose = require('mongoose'),
    Sensor_Data = require('../models/sensor_data'),
    config = require('../config/database');


var functions = {
    add_data: function(req, res) {
        Sensor_Data.findOne({'xvalue': req.body.xvalue}, function(err, data){
            if (err) throw err;
            if (!data){
                // create new data object
                var new_data = Sensor_Data({
                    xvalue: req.body.xvalue,
                    temperature: req.body.temperature,
                    light: req.body.light
                });

                new_data.save(function(err, new_data){
                    if (err){
                        res.json({success:false, msg:'Failed to add datapoint'});
                    }
                    else {
                        res.json({success:true, msg:'Successfully added datapoint'});
                    }
                });
            }
            else {
                // a datapoint with that same xvalue exists...
                res.json({success: false, msg: 'add datapoint failed, username already used.'});
            }
        });
    },


    get_add_datapoints_from_DB: function(req, res) {
        // TODO: limit the number of dpts to return
        Sensor_Data.find(function(err, datapoints) {
            if (err) {
                res.send(err);
            }
            else {
                res.json(datapoints);
            }
        });
    }




};
module.exports = functions;
