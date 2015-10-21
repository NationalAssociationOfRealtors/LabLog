/*!
 * d3.chart.sankey - v0.1.0
 * https://github.com/q-m/d3.chart.sankey/
 *
 * Copyright (c) 2015 wvengen <dev-js@willem.engen.nl>
 * Library released under MIT license.
 */
(function(global, factory) {
	"use strict";

	if (typeof global.define === "function" && global.define.amd) {
		define(["d3"], function(d3) {
			factory(global, d3);
		});
	} else {
		factory(global, global.d3);
	}

})(this, function(window, d3) {
"use strict";

"use strict";
/*jshint node: true */

d3.chart("Sankey.Base", {

  initialize: function() {
    var chart = this;

    // Inspired by d3.chart.layout.hierarchy's hierarchy.js, though also different
    chart.features  = {};
    chart.d3        = {};
    chart.layers    = {};

    chart.base.attr("width",  chart.base.node().parentNode.clientWidth);
    chart.base.attr("height", chart.base.node().parentNode.clientHeight);

    // dimensions, with space for node stroke and labels (smallest at bottom)
    chart.features.margins = {top: 1, right: 1, bottom: 6, left: 1};
    chart.features.width   = chart.base.attr("width") - chart.features.margins.left - chart.features.margins.right;
    chart.features.height  = chart.base.attr("height") - chart.features.margins.top - chart.features.margins.bottom;

    chart.features.name    = function(d) { return d.name; };
    // there is no value property, because we also need to set it on parents
    chart.features.colorNodes = d3.scale.category20c();
    chart.features.colorLinks = null; // css styles by default

    chart.layers.base = chart.base.append("g")
      .attr("transform", "translate(" + chart.features.margins.left + "," + chart.features.margins.top + ")");
  },


  name: function(_) {
    if (!arguments.length) { return this.features.name; }
    this.features.name = _;

    this.trigger("change:name");
    if (this.root) { this.draw(this.root); }

    return this;
  },


  colorNodes: function(_) {
    if (!arguments.length) { return this.features.colorNodes; }
    this.features.colorNodes = _;

    this.trigger("change:color");
    if (this.root) { this.draw(this.root); }

    return this;
  },


  colorLinks: function(_) {
    if (!arguments.length) { return this.features.colorLinks; }
    this.features.colorLinks = _;

    this.trigger("change:color");
    if (this.data) { this.draw(this.data); }

    return this;
  }

});

"use strict";
/*jshint node: true */

d3.chart("Sankey.Base").extend("Sankey", {

  initialize: function() {
    var chart = this;

    chart.d3.sankey = d3.sankey();
    chart.d3.path = chart.d3.sankey.link();
    chart.d3.sankey.size([chart.features.width, chart.features.height]);

    chart.features.spread = false;
    chart.features.iterations = 32;
    chart.features.nodeWidth = chart.d3.sankey.nodeWidth();
    chart.features.nodePadding = chart.d3.sankey.nodePadding();

    chart.layers.links = chart.layers.base.append("g").classed("links", true);
    chart.layers.nodes = chart.layers.base.append("g").classed("nodes", true);


    chart.on("change:sizes", function() {
      chart.d3.sankey.nodeWidth(chart.features.nodeWidth);
      chart.d3.sankey.nodePadding(chart.features.nodePadding);
    });

    chart.layer("links", chart.layers.links, {
      dataBind: function(data) {
        return this.selectAll(".link").data(data.links);
      },

      insert: function() {
        return this.append("path").classed("link", true);
      },

      events: {
        "enter": function() {
          this.on("mouseover", function(e) { chart.trigger("link:mouseover", e); });
          this.on("mouseout",  function(e) { chart.trigger("link:mouseout",  e); });
          this.on("click",     function(e) { chart.trigger("link:click",     e); });
        },

        "merge": function() {
          this
            .attr("d", chart.d3.path)
            .style("stroke", colorLinks)
            .style("stroke-width", function(d) { return Math.max(1, d.dy); })
            .sort(function(a, b) { return b.dy - a.dy; });
        },

        "exit": function() {
          this.remove();
        }
      }
    });

    chart.layer("nodes", chart.layers.nodes, {
      dataBind: function(data) {
        return this.selectAll(".node").data(data.nodes);
      },

      insert: function() {
        return this.append("g").classed("node", true);
      },

      events: {
        "enter": function() {
          this.append("rect");
          this.append("text")
            .attr("dy", ".35em")
            .attr("transform", null);

          this.on("mouseover", function(e) { chart.trigger("node:mouseover", e); });
          this.on("mouseout",  function(e) { chart.trigger("node:mouseout",  e); });
          this.on("click",     function(e) { chart.trigger("node:click",     e); });
        },

        "merge": function() {
          this.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

          this.select("rect")
            .attr("height", function(d) { return d.dy; })
            .attr("width", chart.features.nodeWidth)
            .style("fill", colorNodes)
            .style("stroke", function(d) { return d3.rgb(colorNodes(d)).darker(2); });

          this.select("text")
            .text(chart.features.name)
            .attr("y", function(d) { return d.dy / 2; })
            .attr("x", function(d) { return hasTextLeft(d) ? (6 + chart.features.nodeWidth) : -6; })
            .attr("text-anchor", function(d) { return hasTextLeft(d) ? "start" : "end"; });
        },

        "exit": function() {
          this.remove();
        }
      }
    });

    function hasTextLeft(node) {
      return node.x < chart.features.width / 2;
    }

    function colorNodes(node) {
      if (typeof chart.features.colorNodes === 'function') {
        // allow using d3 scales, but also custom function with node as 2nd argument
        return chart.features.colorNodes(chart.features.name(node), node);
      } else {
        return chart.features.colorNodes;
      }
    }

    function colorLinks(link) {
      if (typeof chart.features.colorLinks === 'function') {
        // always expect custom function, there's no sensible default with d3 scales here
        return chart.features.colorLinks(link);
      } else {
        return chart.features.colorLinks;
      }
    }
  },


  transform: function(data) {
    var chart = this;

    chart.data = data;

    chart.d3.sankey
      .nodes(data.nodes)
      .links(data.links)
      .layout(chart.features.iterations);

    if (this.features.spread) {
      this._spreadNodes(data);
      chart.d3.sankey.relayout();
    }

    return data;
  },


  iterations: function(_) {
    if (!arguments.length) { return this.features.iterations; }
    this.features.iterations = _;

    if (this.data) { this.draw(this.data); }

    return this;
  },


  nodeWidth: function(_) {
    if (!arguments.length) { return this.features.nodeWidth; }
    this.features.nodeWidth = _;

    this.trigger("change:sizes");
    if (this.data) { this.draw(this.data); }

    return this;
  },


  nodePadding: function(_) {
    if (!arguments.length) { return this.features.nodePadding; }
    this.features.nodePadding = _;

    this.trigger("change:sizes");
    if (this.data) { this.draw(this.data); }

    return this;
  },


  spread: function(_) {
    if (!arguments.length) { return this.features.spread; }
    this.features.spread = _;

    if (this.data) { this.draw(this.data); }

    return this;
  },


  _spreadNodes: function(data) {
    var chart = this,
        nodesByBreadth = d3.nest()
        .key(function(d) { return d.x; })
        .entries(data.nodes)
        .map(function(d) { return d.values; });

    nodesByBreadth.forEach(function(nodes) {
      var i,
          node,
          sum = d3.sum(nodes, function(o) { return o.dy; }),
          padding = (chart.features.height - sum) / nodes.length,
          y0 = 0;
      nodes.sort(function(a, b) { return a.y - b.y; });
      for (i = 0; i < nodes.length; ++i) {
        node = nodes[i];
        node.y = y0;
        y0 += node.dy + padding;
      }
    });
  }

});

"use strict";
/*jshint node: true */

// Sankey diagram with a hoverable selection
d3.chart("Sankey").extend("Sankey.Selection", {

  initialize: function() {
    var chart = this;

    chart.features.selection = null;
    chart.features.unselectedOpacity = 0.2;

    chart.on("link:mouseover", chart.selection);
    chart.on("link:mouseout", function() { chart.selection(null); });
    chart.on("node:mouseover", chart.selection);
    chart.on("node:mouseout", function() { chart.selection(null); });

    // going through the whole draw cycle can be a little slow, so we use
    // a selection changed event to update existing nodes directly
    chart.on("change:selection", updateTransition);
    this.layer("links").on("enter", update);
    this.layer("nodes").on("enter", update);

    function update() {
      /*jshint validthis:true */
      if (chart.features.selection && chart.features.selection.length) {
        return this.style("opacity", function(o) {
          return chart.features.selection.indexOf(o) >= 0 ? 1 : chart.features.unselectedOpacity;
        });
      } else {
        return this.style("opacity", 1);
      }
    }

    function updateTransition() {
      var transition = chart.layers.base.selectAll('.node, .link').transition();
      if (!chart.features.selection || !chart.features.selection.length) {
        // short delay for the deselect transition to avoid flicker
        transition = transition.delay(100);
      }
      update.apply(transition.duration(50));
    }
  },

  selection: function(_) {
    if (!arguments.length) { return this.features.selection; }
    this.features.selection = (!_ || _ instanceof Array) ? _ : [_];

    this.trigger("change:selection");

    return this;
  },

  unselectedOpacity: function(_) {
    if (!arguments.length) { return this.features.unselectedOpacity; }
    this.features.unselectedOpacity = _;

    this.trigger("change:selection");

    return this;
  }

});

"use strict";
/*jshint node: true */

// Sankey diagram with a path-hover effect
d3.chart("Sankey.Selection").extend("Sankey.Path", {

  selection: function(_) {
    var chart = this;

    if (!arguments.length) { return chart.features.selection; }
    chart.features.selection = (!_ || _ instanceof Array) ? _ : [_];

    // expand selection with connections
    if (chart.features.selection) {
      chart.features.selection.forEach(function(o) {
        getConnections(o).forEach(function(p) {
          chart.features.selection.push(p);
        });
      });
    }

    chart.trigger("change:selection");

    return chart;
  }

});

function getConnections(o, direction) {
  if (o.source && o.target) {
    return getConnectionsLink(o, direction);
  } else {
    return getConnectionsNode(o, direction);
  }
}

// Return the link and its connected nodes with their links etc.
function getConnectionsLink(o, direction) {
  var links = [o];
  direction = direction || 'both';

  if (direction == 'source' || direction == 'both') {
    links = links.concat(getConnectionsNode(o.source, 'source'));
  }
  if (direction == 'target' || direction == 'both') {
    links = links.concat(getConnectionsNode(o.target, 'target'));
  }

  return links;
}

// Return the node and its connected links. If direction is 'both', just return
// all links; if direction is 'source', only return the source link when there
// is one target link (or none, in which case the node is an endnode); if
// direction is 'target' vice versa. Open the product example to see why.
function getConnectionsNode(o, direction) {
  var links = [o];
  direction = direction || 'both';

  if ((direction == 'source') || direction == 'both') {
    o.targetLinks.forEach(function(p) { links = links.concat(getConnectionsLink(p, direction)); });
  }
  if ((direction == 'target') || direction == 'both') {
    o.sourceLinks.forEach(function(p) { links = links.concat(getConnectionsLink(p, direction)); });
  }

  return links;
}

});
