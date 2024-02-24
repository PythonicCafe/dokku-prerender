function getLogger(name) {
  function log(...args) {
    if (process.env.DISABLE_LOGGING) {
      return;
    }
    console.log(new Date().toISOString(), `[${name}]`, ...args);
  }
  return log;
}

module.exports = { getLogger };
