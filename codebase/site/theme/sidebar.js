(function () {
  "use strict";

  function expandAncestors(element) {
    var node = element.parentElement;
    while (node) {
      if (node.classList?.contains("chapter-item")) {
        node.classList.remove("collapsed");
      }
      node = node.parentElement;
    }
  }

  function setupCollapsibleSidebar() {
    var scrollbox = document.querySelector(".sidebar-scrollbox");
    if (!scrollbox || scrollbox.children.length === 0) return false;

    var currentUrl = window.location.pathname.split("/").pop() || "index.html";

    function isLinkActive(link) {
      if (!link) return false;
      var href = link.getAttribute("href");
      if (!href) return false;
      var hrefFile = href.split("/").pop();
      return hrefFile === currentUrl;
    }

    function hasActiveDescendant(item) {
      var links = item.querySelectorAll("a[href]");
      for (var link of links) {
        var hrefFile = link.getAttribute("href").split("/").pop();
        if (hrefFile === currentUrl) return true;
      }
      return false;
    }

    var chapterItems = scrollbox.querySelectorAll(".chapter-item");
    chapterItems.forEach(function (item) {
      var section = item.querySelector(":scope > ol.section");
      if (!section) return;

      var linkWrapper = item.querySelector(":scope > .chapter-link-wrapper");
      if (item.querySelector(":scope > .sidebar-toggle")) return;

      var toggle = document.createElement("span");
      toggle.className = "sidebar-toggle";
      toggle.setAttribute("aria-label", "Toggle section");

      if (linkWrapper) {
        linkWrapper.before(toggle);
      } else {
        item.prepend(toggle);
      }

      var active = isLinkActive(item.querySelector(":scope > .chapter-link-wrapper > a"));
      var descendantActive = hasActiveDescendant(item);

      if (!active && !descendantActive) {
        item.classList.add("collapsed");
      }

      toggle.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        item.classList.toggle("collapsed");
      });
    });

    var activeLink = scrollbox.querySelector('a[href="' + currentUrl + '"]');
    if (activeLink) {
      expandAncestors(activeLink);
    }

    return true;
  }

  function trySetup(retries) {
    if (setupCollapsibleSidebar()) return;
    if (retries <= 0) return;
    setTimeout(function () {
      trySetup(retries - 1);
    }, 100);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      trySetup(50);
    });
  } else {
    trySetup(50);
  }
})();
