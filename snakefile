MODELRUNS = ["TEMBA_ENB_TAX_High", "TEMBA_ENB_TAX_Low", "TEMBA_ENB_RCP26_dry", "TEMBA_ENB_RCP26_wet", "TEMBA_ENB_RCP60_dry", "TEMBA_ENB_RCP60_wet", "TEMBA_ENB_ref_FPV"]

rule all:
      input: 
             ["results/export_{model_run}/barcharts".format(model_run=model_run) for model_run in MODELRUNS],
	     ["results/export_{model_run}/piecharts".format(model_run=model_run) for model_run in MODELRUNS], 
	     ["results/ScenarioComparison/Mixes_percentages_{model_run}.xlsx".format(model_run=model_run) for model_run in MODELRUNS],
	     ["results/ScenarioComparison/AggregatedExcels/ValuesFPV.xlsx"]
rule generate_model_file:
    input: 
        "input_data/{model_run}.xlsx"
    output: 
        "output_data/{model_run}.txt"
    threads: 
        2
    shell:
        "python scripts/excel_to_osemosys.py {input} {output}"

rule modify_model_file:
    input:  
        "output_data/{model_run}.txt"
    output: 
        "output_data/{model_run}_modex.txt"
    threads: 
        2
    shell:
        "python scripts/CBC_results_AS_MODEX.py {input} && cat {input} > {output}"

rule generate_lp_file:
    input: 
        "output_data/{model_run}_modex.txt"
    output: 
        protected("output_data/{model_run}.lp.gz")
    log: 
        "output_data/glpsol_{model_run}.log"
    threads: 
        1
    shell:
        "glpsol -m model/Temba_0406_modex.txt -d {input} --wlp {output} --check --log {log}"

rule solve_lp:
    input: 
        expand("output_data/{model_run}.lp.gz",model_run=MODELRUNS),
	file="output_data/{model_run}.lp.gz"
    output: 
        protected("output_data/{model_run}.sol")
    log: 
        "output_data/gurobi_{model_run}.log"
    threads: 
        2
    shell:
        "gurobi_cl NumericFocus=1 Method=2 Threads={threads} ResultFile={output} ResultFile=output_data/infeasible.ilp LogFile={log} {input.file}"

rule remove_zero_values:
    input: "output_data/{model_run}.sol"
    output: "results/{model_run}.sol"
    shell:
        "sed '/ * 0$/d' {input} > {output}"

rule generate_pickle:
    input: 
        results="results/{model_run}.sol", modelfile="output_data/{model_run}_modex.txt"
    output: 
        pickle="results/{model_run}.pickle", folder=directory("results/{model_run}")
    shell:
        "mkdir {output.folder} && python scripts/generate_pickle.py {input.modelfile} {input.results} gurobi {output.pickle} {output.folder}"

rule generate_results:
    input: 
        expand("results/{model_run}.pickle", model_run=MODELRUNS),
	pickle="results/{model_run}.pickle"
    params:
        scenario="{model_run}"
    output: 
        folder=directory("results/export_{model_run}/barcharts")
    threads: 1
    conda:
        "envs/results.yaml"
    shell:
        "mkdir {output.folder} && python scripts/generate_results.py {input.pickle} {params.scenario} {output.folder}"

rule create_piecharts:
    input: 
        expand("results/export_{model_run}/barcharts",model_run=MODELRUNS)
    params:
        scenario="{model_run}"
    output: 
        folder=directory("results/export_{model_run}/piecharts")
    conda:
        "envs/results.yaml"
    shell:
        "mkdir {output.folder} && python ResultsCalc.py {input} {params.scenario} {output.folder}"

rule create_comparison_folder:
    input: 
        expand("results/export_{model_run}/piecharts",model_run=MODELRUNS)
    params:
        scenario="{model_run}"
    output: 
        "results/ScenarioComparison/Mixes_percentages_{model_run}.xlsx"
    shell:
        "python rename_files.py {input} {params.scenario} {output}"

rule create_comparison_excels:
    input: 
        expand("results/ScenarioComparison/Mixes_percentages_{model_run}.xlsx",model_run=MODELRUNS)
    params:
        "results/ScenarioComparison"
    output: 
        "results/ScenarioComparison/AggregatedExcels/ValuesFPV.xlsx"
    shell:
        "python create_excels.py {input} {params} {output}"