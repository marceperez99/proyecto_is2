const NODE_RADIUS = 20;
const NODE_COLOR = "#004aba"
function topo_sort(graph){
    let inDegree = graph.reduce((acc,curr)=>({...acc,[curr['codigo']]:0}),{});
    let visited = graph.reduce((acc,curr)=>({...acc,[curr['codigo']]:false}),{});
    let items = graph.reduce((acc,curr)=>({...acc,[curr['codigo']]:curr}),{});

    graph.forEach(u=>{
        u['hijos'].forEach(v=> inDegree[v]++)
    })
    let queue = Object.keys(inDegree).filter(u=>inDegree[u] === 0)
        .map(v=> ({vertice:v,nivel:0}));

    let layers = [];

    while(queue.length){
        let u = queue.shift()
        if(!visited[u.vertice]){
            if (u.nivel >= layers.length) layers.push([]);
            layers[u.nivel].push(u.vertice);
            items[u.vertice].hijos.forEach(v=>{
                inDegree[v]--;
                if(inDegree[v] === 0){
                    queue.push({nivel:u.nivel+1,vertice: v})
                }
            })
        }
    }
    const span = layers.reduce((max,curr)=>Math.max(max,curr.length),0);
    return {layers,width:layers.length,span}
}
function get_coordinates(layering, width, height){
    let coordinates = {};
    let dx = width / (layering.width + 1);

    layering.layers.forEach((layer, i) => {
        let dy = height / (layer.length + 1);
        layer.forEach((node, j) => {
            coordinates[node] = { x: dx * (i + 1), y: dy * (j + 1) }
        })
    });
    return coordinates;
}

function graficar_DAG(data) {
    const layering = data.map(fase=>topo_sort(fase.items));
    let x_offset = 0;
    let divisorias = [];
    let coordenadas = {};

    const svg = d3.select("svg")
                .call(d3.zoom().on("zoom", () => {
                    svg.attr("transform", d3.event.transform)
                }))
                .append("g");
    layering.forEach(layer=> {
        const width = Math.max(2 * NODE_RADIUS * (2 * layer.width + 1), 200);

        const layer_coordinates = Object.entries(get_coordinates(layer, width, 400))
                .reduce((acc, [item, pos]) => ({...acc, [item]: {x: pos.x + x_offset, y: pos.y}}), {});
        x_offset+=width;
        divisorias.push(x_offset);

        coordenadas = {...coordenadas, ...layer_coordinates};
    });
    coordenadas = Object.entries(coordenadas).map(([item, pos]) => ({id:item,x:pos.x,y:pos.y}));
    console.log(coordenadas)
    svg.selectAll("circle")
                .data(coordenadas)
                .enter().append("circle")
                .attr("id", function (d) { return d.id; })
                .attr("cx", function (d) { return d.x; })
                .attr("cy", function (d) { return d.y; })
                .attr("r", NODE_RADIUS)
                .style("fill", function (d, i) { return NODE_COLOR; })
    return layering
}
graficar_DAG(graph)