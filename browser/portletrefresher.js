/*
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziad�<tz@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id:$

javascript layer for tree views
the treeview editor knows how to load nodes dynamically

*/

/* portlet refresher */

var CPSPortletRefresher = Class.create();

CPSPortletRefresher.prototype = {

  initialize: function() {
  },

  refreshPortletCompleted: function(originalRequest) {
    // getting new positions from the server
    result = originalRequest.responseText;

    if (result!='') {
      $(this.last_portlet_id).innerHTML = result;
      var newdiv = document.createElement("div");
      newdiv.innerHTML = result;
      olddiv = $(this.last_portlet_id);
      parent = olddiv.parentNode;
      olddiv.parentNode.replaceChild(newdiv, olddiv);
      newdiv.id = this.last_portlet_id;
    }
  },

  refreshPortlet: function(portlet_id) {
    var params = 'portlet_id=' + portlet_id;
    url = 'viewPortlet';
    var refreshPortletCompletedBn = this.refreshPortletCompleted.bind(this);
    var options = {parameters: params, onComplete: refreshPortletCompletedBn};
    this.last_portlet_id = portlet_id;
    var sender = new Ajax.Request(url, options);
  },
}

var portlet_refresher = new CPSPortletRefresher();


