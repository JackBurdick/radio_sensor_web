var mongoose = require('mongoose');

var Schema = mongoose.Schema;

var sensorData = new Schema(
  {
    xvalue: String,
    temperature: String,
    light: String
  },
  {
    collection: 'home'
  }
);

module.exports = mongoose.model('sensor_data', sensorData);
