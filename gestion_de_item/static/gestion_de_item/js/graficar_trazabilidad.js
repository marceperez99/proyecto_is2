const NODE_RADIUS = 20;
const NODE_COLOR = "#004aba"
const divide_segment_by_ratio = (x1, y1, x2, y2, r) => ({ x: (r * x2 + x1) / (1 + r), y: (r * y2 + y1) / (1 + r), });
const get_edge_arrow = (u, v, radius) => {

    const dx = u.x - v.x;
    const dy = u.y - v.y;
    let r = radius / (Math.sqrt(dx * dx + dy * dy) - radius);
    const startpoint = divide_segment_by_ratio(u.x, u.y, v.x, v.y, r);

    r = (Math.sqrt(dx * dx + dy * dy) - (radius + 7)) / (radius + 7);

    const endpoint = divide_segment_by_ratio(u.x, u.y, v.x, v.y, r);

    return { start: startpoint, end: endpoint }
}

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
const draw_edges = (svg, edges) => {
        const lines = svg.selectAll(".line")
            .data(edges)
            .enter()
            .append("line")
            .attr("x1", d => d.start.x)
            .attr("y1", d => d.start.y)
            .attr("x2", d => d.end.x)
            .attr("y2", d => d.end.y)
            .attr("stroke", "#001638")
            .attr("stroke-width", 2)
            .attr('class', d => `start-${d.start.id} end-${d.end.id}`)
            .attr("marker-end", "url(#arrow)");
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
                .reduce((acc, [item, pos]) => ({...acc, [item]: {
                            x: pos.x + x_offset,
                                y: pos.y,
                                limits:
                                    {
                                        start: x_offset,
                                        end: x_offset + width
                                    }
                        }
                    }), {});
        x_offset+=width;
        divisorias.push(x_offset);

        coordenadas = {...coordenadas, ...layer_coordinates};
    });
    coordenadas_list = Object.entries(coordenadas).map(([item, pos]) => ({id:item,x:pos.x,y:pos.y,limits:pos.limits}));
    console.log(coordenadas)
    const edges = data.reduce((edges, fase) =>
            [...edges,
                ...fase.items.reduce((list, u) =>
                    [
                        ...list,
                        ...u.hijos.map(v => ({start: coordenadas[u.codigo], end:coordenadas[v]})),
                        ...u.sucesores.map(v =>({start: coordenadas[u.codigo], end:coordenadas[v]}))
                    ]
                ,[])
            ]
        ,[]).map(edge => get_edge_arrow(edge.start,edge.end,NODE_RADIUS));
    console.log("->",edges)
    svg.selectAll("circle")
        .data(coordenadas_list)
        .enter().append("circle")
        .attr("id", function (d) { return d.id; })
        .attr("cx", function (d) { return d.x; })
        .attr("cy", function (d) { return d.y; })
        .attr("r", NODE_RADIUS)
        .on("mouseover", function (d) { d3.select(this).style("cursor", "move"); })
        .on("mouseout", function (d) { })
        .call(d3.drag()
            .on('start',function (d) {
                d3.select(this).raise().classed("active", true);
            })
            .on('drag',function(d){
                if (d.limits) {
                    let separator = d.limits
                    if (d3.event.x <= separator.start)
                        d.x = separator.start + NODE_RADIUS + 1;
                    else if (d3.event.x >= separator.end)
                        d.x = separator.end - NODE_RADIUS - 1;
                    else
                        d.x = d3.event.x;
                        } else {
                            d.x = d3.event.x
                        }
                        if (d3.event.y <= NODE_RADIUS) dy = NODE_RADIUS
                        else d.y = d3.event.y
                        d3.select(this).attr("cx", d.x).attr("cy", d.y);
            })
        ).style("fill", function (d, i) { return NODE_COLOR; })
        draw_edges(svg,edges);
    return layering
}
graficar_DAG(graph)