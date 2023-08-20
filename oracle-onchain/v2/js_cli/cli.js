const { program } = require("commander");

program
  .version("1.0.0")
  .description("Lightecho Oracle CLI")
  //.option('-f, --file <filename>', 'Specify a file')
  .command("deploy")
  .description("Deploy a Contract WASM to the Stellar blockchain")
  .argument("<contract_wasm_file_path>")
  .action(function () {
    //this.args[0];
    //this.opts().port;
    console.log("Hello, world!");
  });

program.parse(process.argv);
