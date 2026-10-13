"""Optional Playwright driver for the SDK's structured browser tools."""

from __future__ import annotations

import os
import re
import sys
import json
import time
import base64
import asyncio
import secrets
from socket import inet_aton
from typing import TypeVar, Callable, Awaitable, cast
from ipaddress import IPv4Address, IPv6Address
from contextlib import asynccontextmanager
from collections import deque
from urllib.parse import unquote, urlsplit
from collections.abc import AsyncGenerator
from typing_extensions import Literal

import idna
import httpx2
from owned_pointer import OwnedBrowser, OwnedPointer, OwnedComputer
from playwright.async_api import (
    Page,
    Error,
    Frame,
    Route,
    Dialog,
    Download,
    JSHandle,
    TimeoutError as PlaywrightTimeoutError,
    ElementHandle,
    BrowserContext,
    WebSocketRoute,
    async_playwright,
)

from openai.lib.browser import (
    KeyInput,
    TabInput,
    FindInput,
    TypeInput,
    ZoomInput,
    ClickInput,
    NewTabInput,
    ScrollInput,
    BrowserError,
    BrowserState,
    WaitForInput,
    BrowserReadV1,
    NavigateInput,
    ReadPageInput,
    SelectOptionInput,
    BrowserReadElement,
    BrowserStateChange,
    BrowserScopedReadV1,
    ReadPageScopedInput,
    BrowserCancelledError,
)
from openai.types.responses.response_input_image_content_param import ResponseInputImageContentParam

_Observation = TypeVar("_Observation")

# Same bounded main-document scan as the Node borrowed-context driver.


_BORROWED_READ = r"""function borrowedRead({ nonce, nextRef, full, textOnly, checkedNode, finding = false }) {
  function borrowedReport(report) {
    let output = '';
    let valid = true;
    const append = (piece) => {
      if (output.length + piece.length > 65_536) {
        valid = false;
      } else if (valid) {
        output += piece;
      }
    };
    const quoted = (value) => {
      if (typeof value !== 'string') {
        valid = false;
        return;
      }
      append('"');
      const { length } = value;
      // Literal characters and numeric indices avoid page string iterators/encoders.
      const controls =
        '\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007\u0008\u0009\u000A\u000B\u000C\u000D\u000E\u000F\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017\u0018\u0019\u001A\u001B\u001C\u001D\u001E\u001F';
      const digits = '0123456789abcdef';
      for (let index = 0; valid && index < length; index += 1) {
        const character = value[index];
        if (character === '"' || character === '\\') {
          append(`\\${character}`);
        } else if (character === '\b') {
          append('\\b');
        } else if (character === '\f') {
          append('\\f');
        } else if (character === '\n') {
          append('\\n');
        } else if (character === '\r') {
          append('\\r');
        } else if (character === '\t') {
          append('\\t');
        } else if (character < ' ') {
          for (let control = 0; control < 32; control += 1) {
            if (character === controls[control]) {
              const low = control % 16;
              append(`\\u00${digits[(control - low) / 16]}${digits[low]}`);
              break;
            }
          }
        } else {
          append(character);
        }
      }
      append('"');
    };
    const flag = (value) => {
      if (value === true) {
        append('true');
      } else if (value === false) {
        append('false');
      } else {
        valid = false;
      }
    };
    if (!report || report.version !== 1) {
      return null;
    }
    append('{"version":1,"text":');
    quoted(report.text);
    append(',"elements":[');
    const { elements } = report;
    const count = elements?.length;
    if (typeof count !== 'number' || count < 0 || count > 2000 || count % 1 !== 0) {
      return null;
    }
    for (let index = 0; valid && index < count; index += 1) {
      const item = elements[index];
      if (!item) {
        return null;
      }
      if (index > 0) {
        append(',');
      }
      append('{"ref":');
      quoted(item.ref);
      append(',"role":');
      quoted(item.role);
      append(',"label":');
      quoted(item.label);
      const { value } = item;
      if (value !== undefined) {
        append(',"value":');
        quoted(value);
      }
      const { checked } = item;
      if (checked !== undefined) {
        append(',"checked":');
        flag(checked);
      }
      const { options } = item;
      if (options !== undefined) {
        const size = options?.length;
        if (typeof size !== 'number' || size < 0 || size > 32 || size % 1 !== 0) {
          return null;
        }
        append(',"options":[');
        for (let position = 0; valid && position < size; position += 1) {
          const option = options[position];
          if (!option) {
            return null;
          }
          if (position > 0) {
            append(',');
          }
          append('{"label":');
          quoted(option.label);
          append(',"value":');
          quoted(option.value);
          const { selected } = option;
          if (selected !== undefined) {
            append(',"selected":');
            flag(selected);
          }
          append('}');
        }
        append(']');
      }
      append('}');
    }
    append('],"omitted":[');
    const { omitted } = report;
    const omissions = omitted?.length;
    if (typeof omissions !== 'number' || omissions < 0 || omissions > 2000 || omissions % 1 !== 0) {
      return null;
    }
    for (let index = 0; valid && index < omissions; index += 1) {
      if (index > 0) {
        append(',');
      }
      quoted(omitted[index]);
    }
    append(']}');
    return valid ? output : null;
  }

  const report = {
    __proto__: null,
    version: 1,
    text: '',
    elements: { __proto__: null, length: 0 },
    omitted: { __proto__: null, length: 0 },
  };
  const targets = { __proto__: null, length: 0 };
  const targetLimit = finding || checkedNode ? 2000 : 100;
  // Count UTF-8 bytes without calling a page-owned encoder or string iterator.
  const byteLength = (value) => {
    let bytes = 0;
    for (let index = 0; index < value.length; index += 1) {
      const unit = value[index];
      if (unit <= '\u007F') {
        bytes += 1;
      } else if (unit <= '\u07FF') {
        bytes += 2;
      } else if (
        unit >= '\uD800' && unit <= '\uDBFF' &&
        index + 1 < value.length &&
        value[index + 1] >= '\uDC00' && value[index + 1] <= '\uDFFF'
      ) {
        bytes += 4;
        index += 1;
      } else {
        bytes += 3;
      }
    }
    return bytes;
  };
  let visited = 0;
  let textBytes = 0;
  const omit = (reason) => {
    const { omitted } = report;
    for (let index = 0; index < omitted.length; index += 1) {
      if (omitted[index] === reason) {
        return;
      }
    }
    omitted[omitted.length] = reason;
    omitted.length += 1;
  };
  const bounded = (raw, limit, reason) => {
    let text = '';
    let bytes = 0;
    let inspected = 0;
    // Index primitive strings so page-owned iterators cannot run during a read.
    for (let index = 0; index < raw.length;) {
      if (inspected >= limit) {
        omit(reason);
        break;
      }
      inspected += 1;
      let scalar = raw[index];
      index += 1;
      if (scalar >= '\uD800' && scalar <= '\uDBFF' && index < raw.length && raw[index] >= '\uDC00' && raw[index] <= '\uDFFF') {
        scalar += raw[index];
        index += 1;
      }
      let normalized = scalar;
      if (scalar.length === 1 && (scalar < ' ' || (scalar >= '\u007F' && scalar <= '\u009F') || (scalar >= '\uD800' && scalar <= '\uDFFF'))) {
        if (scalar < '\t' || scalar > '\r') {
          continue;
        }
        normalized = ' ';
      }
      const size = byteLength(normalized);
      if (bytes + size > limit) {
        omit(reason);
        break;
      }
      text += normalized;
      bytes += size;
    }
    return text;
  };
  const labelNames = { __proto__: null, length: 0 };
  const appendText = (node, owner) => {
    if (full) {
      const fragment = bounded(node.data, Math.max(0, 16_384 - textBytes), 'text_limit');
      const addition = bounded(` ${fragment}`, Math.max(0, 16_384 - textBytes), 'text_limit');
      report.text += addition;
      textBytes += byteLength(addition);
    }
    if (owner && !owner.named && owner.labelBytes < 256) {
      const fragment = bounded(node.data, 256 - owner.labelBytes, 'name_limit');
      const addition = bounded(` ${fragment}`, 256 - owner.labelBytes, 'name_limit');
      owner.item.label += addition;
      owner.labelBytes += byteLength(addition);
    }
  };
  // Serialized into the page with borrowedRead.
  // oxlint-disable-next-line consistent-function-scoping
  const hidden = (node) => {
    const style = getComputedStyle(node);
    return (
      node.hidden ||
      Object.hasOwn(node.dataset, 'browserPrivate') ||
      style.display === 'none' ||
      style.visibility === 'hidden' ||
      style.visibility === 'collapse' ||
      Number(style.opacity) === 0
    );
  };
  // oxlint-disable-next-line consistent-function-scoping
  const roleFor = (node, tag) => {
    if (tag === 'select') {
      return node.multiple ? 'listbox' : 'combobox';
    }
    if (tag === 'input') {
      if (['submit', 'button', 'reset', 'image'].includes(node.type)) {
        return 'button';
      }
      if (['checkbox', 'radio'].includes(node.type)) {
        return node.type;
      }
      if (node.type === 'range') {
        return 'slider';
      }
      return 'textbox';
    }
    return tag === 'textarea' || node.isContentEditable ? 'textbox' : 'button';
  };
  const makeTarget = (node, tag) => {
    const role = roleFor(node, tag);
    const name =
      node.getAttribute('aria-label') || node.getAttribute('placeholder') || node.getAttribute('title') || '';
    const label = bounded(name, 256, 'name_limit').trim();
    const item = { __proto__: null, ref: `${nonce}:${nextRef + targets.length + 1}`, role, label };
    if (['input', 'textarea'].includes(tag) && role !== 'button') {
      item.value = bounded(node.value, 512, 'value');
      if (role === 'checkbox' || role === 'radio') {
        item.checked = node.checked;
      }
    }
    if (tag === 'select') {
      item.options = { __proto__: null, length: 0 };
      const options = node.options;
      const count = options.length;
      for (let index = 0; index < count; index += 1) {
        const option = options[index];
        if (visited >= 2000 || item.options.length >= 32) {
          omit('work_limit');
          break;
        }
        visited += 1;
        if (option.matches(':disabled') || hidden(option)) {
          continue;
        }
        const value = bounded(option.value, 512, 'value');
        if (value !== option.value) {
          omit('value');
          continue;
        }
        const optionLabel = bounded(option.label, 256, 'name_limit').trim();
        if (!optionLabel) {
          continue;
        }
        const choice = { __proto__: null, label: optionLabel, value };
        if (role === 'listbox') {
          choice.selected = option.selected;
        } else if (option.selected) {
          item.value = value;
        }
        item.options[item.options.length] = choice;
        item.options.length += 1;
      }
    }
    const target = { __proto__: null, node, item, named: Boolean(label), labelBytes: byteLength(label) };
    targets[targets.length] = target;
    targets.length += 1;
    return target;
  };
  const walk = (node, owner, depth) => {
    if (visited >= 2000 || depth > 64) {
      omit('work_limit');
      return;
    }
    visited += 1;
    if (node.nodeType === Node.TEXT_NODE) {
      appendText(node, owner);
      return;
    }
    if (!(node instanceof HTMLElement) || hidden(node)) {
      return;
    }
    const tag = node.tagName.toLowerCase();
    if (['script', 'style', 'template', 'noscript'].includes(tag)) {
      return;
    }
    const inputType = tag === 'input' ? node.type : null;
    if (inputType === 'password' || inputType === 'file' || inputType === 'hidden') {
      omit('private');
      return;
    }
    let target = owner;
    if (node instanceof HTMLLabelElement && node.control) {
      target = { __proto__: null, item: { __proto__: null, label: '' }, named: false, labelBytes: 0 };
      labelNames[labelNames.length] = { __proto__: null, node: node.control, item: target.item };
      labelNames.length += 1;
    }
    if (
      !textOnly &&
      (node.matches('a[href],button,input,textarea,select,[role=button]') ||
        (node.isContentEditable && !node.parentElement?.isContentEditable))
    ) {
      if (targets.length >= targetLimit) {
        omit('target_limit');
      } else {
        target = makeTarget(node, tag);
      }
    }
    // Do not render textarea/select default text into page text.
    if (['input', 'textarea', 'select'].includes(tag)) {
      return;
    }
    // Recursive visits consume the same global budget.
    // oxlint-disable-next-line no-unmodified-loop-condition
    for (let child = node.firstChild; child && visited < 2000; child = child.nextSibling) {
      walk(child, target, depth + 1);
    }
    if (visited >= 2000) {
      omit('work_limit');
    }
  };
  // Serialized with borrowedRead into the page.
  // oxlint-disable-next-line consistent-function-scoping
  function semanticsFor(target) {
    const { node } = target;
    const form = node.form ?? null;
    return [
      node.tagName,
      node.getAttribute('role'),
      node.getAttribute('type'),
      target.item.role,
      target.item.label,
      target.item.checked ?? null,
      target.item.options ?? null,
      node.matches(':disabled'),
      Boolean(node.readOnly),
      node.getAttribute('href'),
      node.getAttribute('target'),
      node.getAttribute('onclick'),
      node.getAttribute('formaction'),
      node.getAttribute('formmethod'),
      node.getAttribute('formtarget'),
      form?.getAttribute('action') ?? null,
      form?.getAttribute('method') ?? null,
      form?.getAttribute('target') ?? null,
      node.tagName === 'A' || form ? node.baseURI : null,
      node.tagName === 'A' || form ? (document.querySelector('base[target]')?.target ?? null) : null,
      target.item.value ?? null,
    ];
  }
  if (document.body) {
    walk(document.body, null, 0);
  } else {
    omit('unsupported_root');
  }
  const accepted = { __proto__: null };
  let acceptedCount = 0;
  for (let position = 0; position < targets.length; position += 1) {
    const target = targets[position];
    const { node } = target;
    let label = target.item.label.trim();
    if (!label) {
      for (let index = labelNames.length - 1; index >= 0; index -= 1) {
        const associated = labelNames[index];
        if (associated.node === node) {
          label = associated.item.label.trim();
          break;
        }
      }
    }
    target.item.label =
      label ||
      (node instanceof HTMLInputElement && target.item.role === 'button'
        ? bounded(node.type === 'image' ? node.alt : node.value, 256, 'name_limit').trim()
        : '') ||
      target.item.role;
    const semantics = semanticsFor(target);
    if (semantics[7] || semantics[8]) {
      omit('unsupported_control');
      continue;
    }
    // Never store a truncated destination or action as proof of its identity.
    let overLimit = false;
    // oxlint-disable-next-line typescript/prefer-for-of -- Read private fields without page-provided iterators.
    for (let index = 0; index < semantics.length; index += 1) {
      const value = semantics[index];
      if (typeof value === 'string' && value.length > 4096) {
        overLimit = true;
        break;
      }
    }
    if (overLimit) {
      omit('unsupported_control');
      continue;
    }
    if (checkedNode === node) {
      return semantics;
    }
    if (checkedNode) {
      continue;
    }
    report.elements[report.elements.length] = target.item;
    report.elements.length += 1;
    const encoded = borrowedReport(report);
    if (encoded === null || byteLength(encoded) > 65_536) {
      report.elements.length -= 1;
      omit('report_limit');
      break;
    }
    accepted[acceptedCount] = { __proto__: null, node, item: target.item, binding: semantics };
    acceptedCount += 1;
  }
  if (checkedNode) {
    return null;
  }
  return { report: borrowedReport(report), targets: accepted, nextRef: nextRef + targets.length };
}"""

# In-page owned-fixture scan and action use the same bounded visible-name guard.
# Handles and private binding fields stay inside the driver.
_OWNED_ELEMENT = r"""function ownedElement(element, request) {
  function framePathIsVisible(x, y) {
    let view = element.ownerDocument.defaultView;
    let parentX = x;
    let parentY = y;
    try {
      while (view !== view.top) {
        const frame = view.frameElement;
        // Cross-origin frameElement is null. Its parent hit test cannot be proved.
        if (!frame || frame.clientWidth !== view.innerWidth || frame.clientHeight !== view.innerHeight) {
          return false;
        }
        const { parent } = view;
        for (
          let node = frame;
          node;
          node = node.assignedSlot ?? node.parentElement ?? node.getRootNode().host ?? null
        ) {
          if (!charge()) {
            return false;
          }
          const style = parent.getComputedStyle(node);
          if (Object.hasOwn(node.dataset, 'browserPrivate')) {
            omit('private');
            return false;
          }
          // Coordinates below support untransformed frame paths only.
          if (
            style.transform !== 'none' ||
            style.scale !== 'none' ||
            style.rotate !== 'none' ||
            style.translate !== 'none' ||
            style.perspective !== 'none' ||
            !['1', 'normal'].includes(style.zoom) ||
            Number(style.opacity) === 0
          ) {
            return false;
          }
        }
        const box = frame.getBoundingClientRect();
        parentX += box.left + frame.clientLeft;
        parentY += box.top + frame.clientTop;
        if (parent.document.elementFromPoint(parentX, parentY) !== frame) {
          return false;
        }
        view = parent;
      }
      return true;
    } catch {
      // An inaccessible ancestor is unsupported; no DOM action was dispatched.
      return false;
    }
  }
  const report = request.report ?? { version: 1, text: '', elements: [], omitted: [] };
  let visited = request.visited ?? 0;
  const omit = (reason) => {
    if (!report.omitted.includes(reason)) {
      report.omitted.push(reason);
    }
  };
  const charge = () => {
    if (visited >= 2000) {
      omit('work_limit');
      return false;
    }
    visited += 1;
    return true;
  };
  // oxlint-disable-next-line consistent-function-scoping
  const parent = (node) => node.assignedSlot ?? node.parentElement ?? node.getRootNode().host ?? null;
  // oxlint-disable-next-line consistent-function-scoping
  const normalize = (text) => text.replaceAll(/\s+/gu, ' ').trim();
  const bounded = (text, limit, reason) => {
    let value = '';
    let bytes = 0;
    for (const scalar of text) {
      const point = scalar.codePointAt(0);
      const size = new TextEncoder().encode(scalar).length;
      if ((point >= 0xd8_00 && point <= 0xdf_ff) || bytes + size > limit) {
        omit(reason);
        break;
      }
      value += scalar;
      bytes += size;
    }
    return value;
  };
  function visible(node) {
    for (let current = node; current; current = parent(current)) {
      if (!charge()) {
        return false;
      }
      const style = getComputedStyle(current);
      const inputType = current instanceof HTMLInputElement ? current.type : null;
      if (
        Object.hasOwn(current.dataset, 'browserPrivate') ||
        inputType === 'password' || inputType === 'file' || inputType === 'hidden'
      ) {
        omit('private');
        return false;
      }
      if (
        style.display === 'none' ||
        style.visibility !== 'visible' ||
        Number(style.opacity) === 0 ||
        current.hidden
      ) {
        omit('private');
        return false;
      }
    }
    return true;
  }
  function isReady(target) {
    if (!visible(target)) {
      return false;
    }
    const box = target.getBoundingClientRect();
    const x = box.x + box.width / 2;
    const y = box.y + box.height / 2;
    // Document hit-testing returns the host for an open shadow target.
    // Follow the same point through each inspectable root, never a selector.
    let at = document.elementFromPoint(x, y);
    while (at?.shadowRoot) {
      const deeper = at.shadowRoot.elementFromPoint(x, y);
      if (!deeper || deeper === at) {
        break;
      }
      at = deeper;
    }
    if (request.action === 'scroll_to') {
      // A viewport alone cannot prove which surface would receive a scroll.
      let clipped = false;
      for (let current = target; current; current = parent(current)) {
        if (!charge()) {
          return false;
        }
        const style = getComputedStyle(current);
        if (style.transform !== 'none' || style.scale !== 'none' || style.rotate !== 'none' ||
            style.translate !== 'none' || style.perspective !== 'none' || !['1', 'normal'].includes(style.zoom)) {
          return false;
        }
        const rect = current.getBoundingClientRect();
        const portLeft = rect.left + current.clientLeft;
        const portTop = rect.top + current.clientTop;
        for (const [overflow, outside, scrollable] of [
          [style.overflowX, x < portLeft || x >= portLeft + current.clientWidth, current.scrollWidth > current.clientWidth],
          [style.overflowY, y < portTop || y >= portTop + current.clientHeight, current.scrollHeight > current.clientHeight],
        ]) {
          if (outside && overflow === 'clip') {
            return false;
          }
          if (outside && ['auto', 'scroll', 'hidden'].includes(overflow)) {
            const left = Math.max(0, portLeft);
            const top = Math.max(0, portTop);
            const right = Math.min(innerWidth, portLeft + current.clientWidth);
            const bottom = Math.min(innerHeight, portTop + current.clientHeight);
            const px = (left + right) / 2, py = (top + bottom) / 2;
            let hit = current.getRootNode().elementFromPoint(px, py);
            if (!scrollable || left >= right || top >= bottom || !hit || !visible(hit) || !framePathIsVisible(px, py)) {
              return false;
            }
            // Ordinary content in flow (e.g. a spacer) may cover this point.
            // Positioned or transformed non-ancestors can be overlays, even
            // when inserted inside the scroll port. Refuse that unsupported case.
            while (hit && hit !== current) {
              if (!charge()) {
                return false;
              }
              const painted = getComputedStyle(hit);
              if (!hit.contains(target) && (painted.position !== 'static' || painted.zIndex !== 'auto' ||
                  painted.transform !== 'none' || painted.scale !== 'none' || painted.rotate !== 'none' ||
                  painted.translate !== 'none' || painted.perspective !== 'none' ||
                  !['1', 'normal'].includes(painted.zoom))) {
                return false;
              }
              hit = parent(hit);
            }
            if (hit !== current) {
              return false;
            }
            clipped = true;
          }
        }
      }
      return !!(box.width && box.height && !target.matches(':disabled') && !target.readOnly &&
        (clipped || (at && (at === target || target.contains(at)) && framePathIsVisible(x, y))));
    }
    return !!(
      box.width &&
      box.height &&
      x >= 0 &&
      y >= 0 &&
      x < innerWidth &&
      y < innerHeight &&
      at &&
      (at === target || target.contains(at)) &&
      !target.matches(':disabled') &&
      !target.readOnly &&
      (request.remote || framePathIsVisible(x, y))
    );
  }
  function rendered(root, label = false) {
    let text = '';
    function walk(node) {
      if (!charge()) {
        return;
      }
      if (node.nodeType === Node.TEXT_NODE) {
        const container = node.parentElement;
        if (container && visible(container)) {
          text = bounded(text + node.data, label ? 256 : 16_384, label ? 'name_limit' : 'text_limit');
        }
        return;
      }
      if (!(node instanceof Element) || !visible(node)) {
        return;
      }
      // Embedded values and scripts never supply a rendered label or page text.
      if (
        ['SCRIPT', 'STYLE', 'TEMPLATE', 'INPUT', 'TEXTAREA', 'SELECT'].includes(node.tagName) ||
        (node.tagName === 'OPTION' && node !== root)
      ) {
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(node.tagName)) {
          omit('value');
        }
        return;
      }
      for (let child = node.firstChild; child; child = child.nextSibling) {
        if (visited >= 2000) {
          break;
        }
        walk(child);
      }
    }
    walk(root);
    return normalize(text);
  }
  function nameOf(target) {
    const root = target.getRootNode();
    let label = '';
    const labelled = target.getAttribute('aria-labelledby');
    if (labelled) {
      // Limit ID lookup before iterating, never read recursive labelledby.
      let count = 0;
      for (const id of labelled.matchAll(/\S+/gu)) {
        if (count === 8) {
          omit('name_limit');
          break;
        }
        count += 1;
        if (!charge()) {
          break;
        }
        // Native ID lookup stays in this root and never parses a selector from page text.
        // oxlint-disable-next-line unicorn/prefer-query-selector
        const source = root.getElementById(id[0]);
        if (source && visible(source)) {
          label += ` ${rendered(source, true)}`;
        }
      }
    }
    if (!normalize(label)) {
      label = target.getAttribute('aria-label') ?? '';
    }
    if (!normalize(label) && target.labels) {
      for (let index = 0; index < Math.min(target.labels.length, 8); index += 1) {
        if (!charge()) {
          break;
        }
        const source = target.labels[index];
        if (visible(source)) {
          label += ` ${rendered(source, true)}`;
        }
      }
      if (target.labels.length > 8) {
        omit('name_limit');
      }
    }
    if (!normalize(label)) {
      label = rendered(target, true);
    }
    if (!normalize(label)) {
      label = target.getAttribute('placeholder') ?? '';
    }
    label = bounded(normalize(label), 256, 'name_limit');
    return label;
  }
  function observe(target) {
    const supported =
      target instanceof HTMLButtonElement ||
      target instanceof HTMLTextAreaElement ||
      (target instanceof HTMLInputElement && ['text', 'date', 'range', 'checkbox', 'radio'].includes(target.type)) ||
      target instanceof HTMLSelectElement;
    if (!supported) {
      if (
        target.matches('input,textarea,select,button,[role=button],[contenteditable=true],a[href]') &&
        visible(target)
      ) {
        omit('unsupported_control');
      }
      return null;
    }
    let row = target;
    while (row && !Object.hasOwn(row.dataset, 'recordId')) {
      if (!charge()) {
        return null;
      }
      row = parent(row);
    }
    if (!row || !target.isConnected || target.ownerDocument !== document || !isReady(target)) {
      return null;
    }
    const label = nameOf(target);
    if (!label) {
      omit('unsupported_control');
      return null;
    }
    let role = 'textbox';
    if (target instanceof HTMLButtonElement) {
      role = 'button';
    } else if (target instanceof HTMLSelectElement) {
      role = target.multiple ? 'listbox' : 'combobox';
    } else if (target instanceof HTMLInputElement) {
      if (target.type === 'checkbox' || target.type === 'radio') role = target.type;
      if (target.type === 'range') role = 'slider';
    }
    const result = {
      record: row.dataset.recordId,
      tag: target.tagName.toLowerCase(),
      rawRole: target.getAttribute('role'),
      role,
      label,
      field: target.dataset.browserField ?? null,
      controlType: target.type ?? null,
      group: null,
      checked: null,
      formOwner: role === 'radio' && target.name ? target.form : null,
    };
    if (role === 'checkbox' || role === 'radio') result.checked = target.checked;
    if (role === 'radio' && target.name) {
      // Native groups include external form-associated controls, but do not
      // cross tree roots. An empty name is not a native radio group.
      const group = [];
      const walk = document.createTreeWalker(target.getRootNode(), NodeFilter.SHOW_ELEMENT);
      let peer;
      while ((peer = walk.nextNode())) {
        if (!charge()) return null;
        if (!(peer instanceof HTMLInputElement) || peer.type !== 'radio' ||
            peer.name !== target.name || peer.form !== target.form) continue;
        let peerRow = peer;
        while (peerRow && !Object.hasOwn(peerRow.dataset, 'recordId')) {
          if (!charge()) return null;
          peerRow = parent(peerRow);
        }
        if (!peerRow || peerRow !== row || !isReady(peer)) return null;
        group.push([peer.dataset.browserField ?? null, nameOf(peer), peer.checked]);
      }
      result.group = JSON.stringify([target.name, target.form?.id ?? null, group]);
    }
    return result;
  }
  if (request.action === 'scan') {
    const targets = [];
    // No trusted inventory can prove a closed root absent in these fixtures.
    omit('unsupported_root');
    const fits = () =>
      new TextEncoder().encode(
        JSON.stringify({
          ...report,
          // A later frame can add any omission after this entry is accepted.
          omitted: [
            'report_limit',
            'text_limit',
            'target_limit',
            'work_limit',
            'frame_limit',
            'unsupported_root',
            'unsupported_control',
            'remote_action',
            'private',
            'value',
            'name_limit',
          ],
        }),
      ).length <= 65_536;
    const scopeLabel = (node) => {
      if (
        !node.isConnected ||
        node.ownerDocument !== document ||
        !(['SECTION', 'ARTICLE', 'NAV'].includes(node.tagName) || node.getAttribute('role') === 'region') ||
        !visible(node)
      ) {
        return null;
      }
      const rect = node.getBoundingClientRect();
      if (!rect.width || !rect.height) {
        return null;
      }
      const label = bounded(normalize(node.getAttribute('aria-label') ?? ''), 256, 'name_limit');
      return label || null;
    };
    if (request.scopeRoot && scopeLabel(element) !== request.expected.label) {
      throw new Error('Scope changed during the read.');
    }
    const addText = (value) => {
      const previous = report.text;
      report.text = bounded(normalize(`${previous} ${value}`), 16_384, 'text_limit');
      if (!fits()) {
        report.text = previous;
        omit('report_limit');
      }
    };
    const publicValues = new Set(request.publicValues);
    // Keep value consent and whole-report admission next to the actual emitted entry.
    // oxlint-disable-next-line complexity
    const addTarget = (node) => {
      const observation = request.textOnly ? null : observe(node);
      if (observation && (!request.query || observation.label.toLowerCase().includes(request.query))) {
        const item = {
          ref: `${request.nonce}:${request.nextRef + targets.length + 1}`,
          role: observation.role,
          label: observation.label,
        };
        if (node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement) {
          const permitted = publicValues.has(JSON.stringify([document.URL, observation.record, observation.field]));
          if (permitted) {
            if (observation.role === 'checkbox' || observation.role === 'radio') {
              item.checked = node.checked;
            } else if (!(node instanceof HTMLSelectElement) ||
                       (!node.multiple && (node.selectedIndex < 0 || visible(node.options[node.selectedIndex])))) {
              item.value = bounded(node.value, 512, 'value');
            } else if (!node.multiple) {
              omit('value');
            }
            if (node instanceof HTMLSelectElement) {
              item.options = [];
              for (const option of node.options) {
                if (!charge()) {
                  break;
                }
                if (item.options.length === 32) {
                  omit('target_limit');
                  break;
                }
                if (!visible(option)) {
                  continue;
                }
                const label = rendered(option, true);
                if (!label) {
                  omit('name_limit');
                  continue;
                }
                const value = bounded(option.value, 512, 'value');
                if (value !== option.value) continue;
                const selected = { label, value };
                if (node.multiple) selected.selected = option.selected;
                item.options.push(selected);
              }
            }
          } else {
            omit('value');
          }
        }
        if (request.remote && targets.length >= 100) {
          omit('target_limit');
        } else if (request.remote) {
          omit('remote_action');
          const box = node.getBoundingClientRect();
          targets.push({ node, observation, item, x: box.x + box.width / 2, y: box.y + box.height / 2 });
        } else if (report.elements.length >= 100) {
          omit('target_limit');
        } else {
          report.elements.push(item);
          if (fits()) {
            targets.push({ node, observation, item });
          } else {
            report.elements.pop();
            omit('report_limit');
          }
        }
      }
    };
    const addScope = (node) => {
      if (!report.scopes || (request.scopeRoot && node === element)) {
        return;
      }
      const label = scopeLabel(node);
      if (label === null) {
        return;
      }
      if (report.scopes.length >= 100) {
        omit('target_limit');
        return;
      }
      const item = { ref: `${request.nonce}:${request.nextRef + targets.length + 1}`, label };
      report.scopes.push(item);
      if (fits()) {
        targets.push({ node, observation: { label }, item, scope: true });
      } else {
        report.scopes.pop();
        omit('report_limit');
      }
    };
    const walk = (node, depth, domDepth) => {
      if (!charge()) {
        return;
      }
      if (depth > 8) {
        omit('frame_limit');
        return;
      }
      if (request.domDepth !== undefined && domDepth > request.domDepth) {
        omit('unsupported_root');
        return;
      }
      if (node.nodeType === Node.TEXT_NODE) {
        if (request.full && !request.remote && node.parentElement && visible(node.parentElement)) {
          if (window !== window.top) {
            const range = document.createRange();
            range.selectNodeContents(node);
            const rect = range.getBoundingClientRect();
            if (!rect.width || !rect.height ||
                !framePathIsVisible(rect.left + rect.width / 2, rect.top + rect.height / 2)) {
              return;
            }
          }
          addText(node.data);
        }
        return;
      }
      if (!(node instanceof Element) || !visible(node)) {
        return;
      }
      // Current field values require an immutable launcher declaration.
      if (request.textOnly && ['INPUT', 'TEXTAREA', 'SELECT'].includes(node.tagName)) {
        omit('value');
      }
      addScope(node);
      addTarget(node);
      if (['SCRIPT', 'STYLE', 'TEMPLATE', 'INPUT', 'TEXTAREA', 'SELECT', 'OPTION'].includes(node.tagName)) {
        return;
      }
      if (node.shadowRoot) {
        for (let child = node.shadowRoot.firstChild; child; child = child.nextSibling) {
          if (visited >= 2000) {
            break;
          }
          walk(child, depth + 1, domDepth + 1);
        }
      }
      for (let child = node.firstChild; child; child = child.nextSibling) {
        if (visited >= 2000) {
          break;
        }
        // Light DOM under an open host renders only if assigned to a slot.
        // Visit every sibling without materializing assignedNodes(), including nonrendered ones.
        if (node.shadowRoot && !child.assignedSlot) {
          charge();
          continue;
        }
        walk(child, depth, domDepth + 1);
      }
    };
    walk(element, request.depth, 0);
    if (visited >= 2000) {
      omit('work_limit');
    }
    return { report, targets, visited };
  }
  function applyAction() {
    if (request.action === 'set_checked' && element instanceof HTMLInputElement && element.type === 'checkbox') {
      if (element.checked !== request.checked) {
        HTMLElement.prototype.click.call(element);
        if (!sameTarget(observe(element)) ||
            visited >= 2000 || element.checked !== request.checked) {
          throw new Error('Owned checkbox changed or refused the requested state after input.');
        }
      }
      return true;
    }
    if (request.action === 'scroll_to') {
      Element.prototype.scrollIntoView.call(element, {behavior:'instant', block:'nearest', inline:'nearest'});
      return true;
    }
    if (request.action === 'click' && element instanceof HTMLButtonElement) {
      if (element.type === 'submit' && element.form) {
        const fields = Object.getOwnPropertyDescriptor(HTMLFormElement.prototype, 'elements').get.call(element.form);
        for (let index = 0; index < fields.length; index += 1) {
          if (!charge()) return null;
          const field = fields.item(index);
          if (field.willValidate && !field.validity.valid) return null;
        }
      }
      HTMLElement.prototype.click.call(element);
      return true;
    }
    if (request.action === 'click' && element instanceof HTMLInputElement &&
        ['checkbox', 'radio'].includes(element.type)) {
      HTMLElement.prototype.click.call(element);
      return true;
    }
    if (request.action === 'type' && (element instanceof HTMLTextAreaElement ||
        (element instanceof HTMLInputElement && ['text', 'date', 'range'].includes(element.type)))) {
      const native = element instanceof HTMLTextAreaElement ? HTMLTextAreaElement : HTMLInputElement;
      const setter = Object.getOwnPropertyDescriptor(native.prototype, 'value').set;
      const constrained = element instanceof HTMLInputElement && ['date', 'range'].includes(element.type);
      if (constrained) {
        const candidate = document.createElement('input');
        candidate.type = element.type;
        candidate.min = element.min;
        candidate.max = element.max;
        candidate.step = element.step;
        candidate.required = element.required;
        // HTML uses the value content attribute as a step base when min is
        // absent. The mutable current value is not that base.
        const valueAttribute = element.getAttribute('value');
        if (valueAttribute !== null) candidate.setAttribute('value', valueAttribute);
        setter.call(candidate, request.text);
        if (element.type === 'date' && candidate.value !== request.text) return 'invalid_native_date';
        if (candidate.value !== request.text || !candidate.validity.valid) return null;
      }
      setter.call(element, request.text);
      element.dispatchEvent(new Event('input', { bubbles: true }));
      if (constrained) changed();
      if (!sameTarget(observe(element)) || element.value !== request.text) {
        throw new Error('Owned text field changed or refused the requested value after input.');
      }
      return true;
    }
    if (request.action === 'select_option' && element instanceof HTMLSelectElement) {
      const requested = new Set(request.values);
      if (requested.size !== request.values.length || (!element.multiple && requested.size !== 1)) return null;
      const matches = new Set();
      const affected = [];
      const count = element.options.length;
      for (let index = 0; index < count; index += 1) {
        if (!charge()) return null;
        const option = element.options[index], next = requested.has(option.value);
        if (next) {
          if (matches.has(option.value)) return null;
          matches.add(option.value);
        }
        if (next || option.selected) {
          if (option.disabled || option.parentElement?.matches('optgroup:disabled') || !visible(option)) return null;
        }
        if (next !== option.selected) affected.push([option, next]);
      }
      if (matches.size !== requested.size) return null;
      if (element.multiple) {
        const setter = Object.getOwnPropertyDescriptor(HTMLOptionElement.prototype, 'selected').set;
        for (const [option, next] of affected) setter.call(option, next);
      } else {
        Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set.call(element, request.values[0]);
      }
      element.dispatchEvent(new Event('input', { bubbles: true }));
      changed();
      const selected = new Set();
      for (const option of element.options) {
        if (!charge()) throw new Error('Owned select exceeded the observation budget after input.');
        if (option.selected) selected.add(option.value);
      }
      if (!sameTarget(observe(element)) || selected.size !== requested.size ||
          [...requested].some((value) => !selected.has(value))) {
        throw new Error('Owned select changed or refused the requested values after input.');
      }
      return true;
    }
    return null;
  }
  function sameTarget(observation) {
    return observation && request.expected.record === observation.record &&
      request.expected.tag === observation.tag && request.expected.label === observation.label &&
      request.expected.role === observation.role && request.expected.rawRole === observation.rawRole &&
      request.expected.field === observation.field && request.expected.controlType === observation.controlType &&
      request.expected.formOwner === observation.formOwner;
  }
  function changed() {
    // Input listeners run synchronously. Never send change to a recycled row.
    // The operation has already affected the page; an unconfirmed remainder
    // retires the owned context rather than returning a pre-effect refusal.
    if (!sameTarget(observe(element))) throw new Error('Owned control changed during input.');
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }
  const observation = observe(element);
  if (!observation || visited >= 2000) {
    return null;
  }
  if (request.action === 'read') {
    return observation;
  }
  const alreadySet = request.action === 'set_checked' && observation.checked === request.checked;
  if (!sameTarget(observation) || (!alreadySet && request.expected.checked !== observation.checked) ||
      request.expected.group !== observation.group) {
    return null;
  }
  if (request.action === 'describe') {
    return {label:observation.label, role:observation.role};
  }
  return applyAction();
}
"""
_OWNED_ACT = "(e, saved) => (" + _OWNED_ELEMENT + ")(e, {...saved, expected:saved.binding}) ?? false"


def _serialize_binding(value: object, item: BrowserReadElement | None = None) -> str:
    if not isinstance(value, list):
        raise BrowserError("Browser changed during the read. Read again.")
    parts = cast(list[object], value).copy()
    if len(parts) < 7:
        raise BrowserError("Browser changed during the read. Read again.")
    private_options = parts[6]
    if private_options is not None:
        if not isinstance(private_options, dict):
            raise BrowserError("Browser changed during the read. Read again.")
        private_options = cast(dict[str, object], private_options)
        count = private_options.get("length")
        if not isinstance(count, int) or isinstance(count, bool) or count < 0 or count > 32:
            raise BrowserError("Browser changed during the read. Read again.")
        parts[6] = [private_options.get(str(index)) for index in range(count)]
    if item is not None:
        if len(parts) < 21 or parts[20] != item.get("value"):
            raise BrowserError("Browser changed during the read. Read again.")
        parts[3:7] = [item["role"], item["label"], item.get("checked"), item.get("options")]
    # Keep a read's value out of the stable identity of a reusable control.
    del parts[20:]
    if isinstance(parts[6], list):
        options = cast(list[object], parts[6])
        pairs: list[list[object]] = []
        for option in options:
            if not isinstance(option, dict):
                raise BrowserError("Browser changed during the read. Read again.")
            fields = cast(dict[str, object], option)
            pairs.append([fields.get("label"), fields.get("value")])
        parts[6] = pairs
    return json.dumps(parts, ensure_ascii=False, separators=(",", ":"))


async def _check_borrowed_input(handle: ElementHandle) -> None:
    # Playwright's native CSS engine uses its utility world, independent of main-world input properties.
    private_input = await handle.query_selector(
        'css=:scope:is(input[type="password" i], input[type="file" i], input[type="hidden" i])'
    )
    if private_input is not None:
        await private_input.dispose()
        raise BrowserError("Browser changed during the read. Read again.")


_PARENT_VISIBLE = """(element, at) => {
  const parent = node => node.assignedSlot ?? node.parentElement ?? node.getRootNode().host ?? null;
  let count = at.visited;
  for (let node = element; node; node = parent(node)) {
    if (count >= 2000) return {point:null, count};
    count += 1;
    const style = getComputedStyle(node);
    if (node.hasAttribute('data-browser-private') || node.hidden ||
        style.display === 'none' || style.visibility !== 'visible' ||
        Number(style.opacity) === 0 || style.transform !== 'none' || style.scale !== 'none' ||
        style.rotate !== 'none' || style.translate !== 'none' || style.perspective !== 'none' ||
        !['1', 'normal'].includes(style.zoom)) return {point:null, count};
  }
  const box = element.getBoundingClientRect();
  const x = box.left + element.clientLeft + at.x, y = box.top + element.clientTop + at.y;
  if (at.x < 0 || at.y < 0 || at.x >= element.clientWidth || at.y >= element.clientHeight ||
      document.elementFromPoint(x, y) !== element) return {point:null, count};
  return {point:{x,y}, count};
}"""


def example_browser_channel() -> Literal["chrome"] | None:
    channel = os.environ.get("OPENAI_EXAMPLE_BROWSER_CHANNEL")
    if channel is None:
        return None
    if channel != "chrome":
        raise ValueError("OPENAI_EXAMPLE_BROWSER_CHANNEL must be unset or chrome.")
    return "chrome"


def _reported_url(value: str) -> str:
    if value == "about:blank":
        return value
    parsed = urlsplit(value)
    if not parsed.scheme:
        raise BrowserError("Browser URL is invalid.")
    if parsed.scheme in ("http", "https"):
        authority = parsed.netloc.rsplit("@", 1)[-1]
        if not authority:
            raise BrowserError("Browser URL is invalid.")
        normalized = httpx2.URL(f"{parsed.scheme}://{authority}")
        projected = f"{normalized.scheme}://{normalized.netloc.decode('ascii')}"
    else:
        projected = parsed.scheme + ":"
    if len(projected.encode("utf-8")) > 2048:
        raise BrowserError("Browser URL exceeds the supported state budget.")
    return projected


def origin(url: str) -> str:
    try:
        parsed = urlsplit(url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ValueError
        host = parsed.hostname
        if parsed.netloc.startswith("["):
            if "%" in host:
                raise ValueError
            host = f"[{IPv6Address(host).compressed}]"
        else:
            host = idna.uts46_remap(unquote(host, errors="strict"), std3_rules=False, transitional=False)
            if not host or any(ord(c) <= 32 or c in "#%/:<>?@[\\]^|" or ord(c) == 127 for c in host):
                raise ValueError
            if not host.isascii():
                host = idna.encode(host).decode("ascii")
            last = host.removesuffix(".").rsplit(".", 1)[-1]
            if re.fullmatch(r"(?:[0-9]+|0[xX][0-9a-fA-F]*)", last):
                host = str(IPv4Address(inet_aton(host.removesuffix("."))))
        port = parsed.port if parsed.port is not None else (443 if parsed.scheme == "https" else 80)
        return f"{parsed.scheme}://{host}:{port}"
    except (ValueError, OSError):
        raise BrowserError("Only HTTP(S) URLs without credentials are supported.") from None


def _exact_fixture_url(value: str) -> bool:
    if type(value) is not str or "#" in value or "\\" in value:
        return False
    try:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        last_label = host.removesuffix(".").split(".")[-1]
        if re.fullmatch(r"(?:[0-9]+|0x[0-9a-f]*)", last_label):
            if str(IPv4Address(host)) != host:
                return False
        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.hostname and parsed.path)
            and not parsed.username
            and not parsed.password
            and not any(unquote(segment) in {".", ".."} for segment in parsed.path.split("/"))
            and str(httpx2.URL(value)) == value
        )
    except (ValueError, httpx2.InvalidURL):
        return False


class PlaywrightBrowser:
    """One disposable context with tab-local element handles and fresh refs per read.

    This example guards direct requests and rejects redirects. It is not a
    network sandbox; deploy untrusted browsing with environment network controls.
    """

    def __init__(
        self,
        context: BrowserContext,
        allowed_origins: set[str],
        *,
        owned_fixture_urls: frozenset[str] | None = None,
        public_values: frozenset[tuple[str, str, str]] = frozenset(),
        public_viewports: frozenset[str] = frozenset(),
    ) -> None:
        """owned_fixture_urls explicitly delegates closure of this context.

        Only pass it for a context created for installed owned fixtures, never
        a borrowed session. open_browser creates and delegates its new context.
        """
        self.context = context
        self.allowed_origins = frozenset(allowed_origins)
        if owned_fixture_urls is not None and (
            not owned_fixture_urls
            or any(not _exact_fixture_url(url) or not self.allows(url) for url in owned_fixture_urls)
        ):
            raise ValueError("Owned fixtures require exact installed HTTP(S) URLs in the allowed origins.")
        if any(
            type(entry) is not tuple
            or len(entry) != 3
            or any(
                type(value) is not str or not value or any(0xD800 <= ord(char) <= 0xDFFF for char in value)
                for value in entry
            )
            or owned_fixture_urls is None
            or entry[0] not in owned_fixture_urls
            for entry in public_values
        ):
            raise ValueError("Public values require an exact owned document URL, record and field.")
        self.owned_fixture_urls = owned_fixture_urls
        if owned_fixture_urls is not None and context.pages:
            raise ValueError("Owned fixtures require a new empty context, not a borrowed browser session.")
        self.public_values = tuple(
            json.dumps(entry, ensure_ascii=False, separators=(",", ":")) for entry in public_values
        )
        if type(public_viewports) is not frozenset or any(
            type(url) is not str or owned_fixture_urls is None or url not in owned_fixture_urls
            for url in public_viewports
        ):
            raise ValueError("Public viewports must be exact installed owned URLs.")
        self.public_viewports = frozenset(public_viewports)
        self._pointer = OwnedPointer(self)
        self._retirement: asyncio.Task[None] | None = None
        self._unusable = False
        self._reference_action_active = False
        self._nonce = secrets.token_hex(16)
        self._next_ref = 0
        self._sequence = 0
        self._changes: deque[BrowserStateChange] = deque(maxlen=32)
        self.tabs: dict[str, Page] = {}
        self._page_generations: dict[str, int] = {}
        self.active = ""
        self._next_tab = 0
        self._generation = 0
        self._refs: dict[str, dict[str, tuple[ElementHandle, object, int]]] = {}
        context.on("page", self._register)
        context.on("close", lambda _context: self._retired())
        for page in context.pages:
            self._register(page)

    def _register(self, page: Page) -> None:
        if self._unusable or page in self.tabs.values():
            return
        if self.owned_fixture_urls is not None and len(self.tabs) >= 100:
            self._retired()
            self._retirement = asyncio.create_task(self.context.close())
            self._retirement.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
            return
        self._next_tab += 1
        tab_id = str(self._next_tab)
        self.tabs[tab_id] = page
        self._page_generations[tab_id] = 0
        self.active = tab_id
        self._refs[tab_id] = {}
        page.set_default_timeout(5_000)
        self._notice("tab_opened", tab_id)
        page.on("framenavigated", lambda _frame: self._notice("navigation", tab_id))
        page.on("framedetached", lambda _frame: self._revoke(tab_id))
        page.on("close", lambda _page: self._closed_tab(tab_id))
        if self.owned_fixture_urls is not None:
            page.on("dialog", lambda dialog: self._dismiss(dialog, tab_id))
            page.on("download", lambda download: self._download(download, tab_id))

    def _closed_tab(self, tab_id: str) -> None:
        self._notice("tab_closed", tab_id)
        self.tabs.pop(tab_id, None)
        self._page_generations.pop(tab_id, None)
        self._refs.pop(tab_id, None)

    def _usable(self) -> None:
        if self._unusable:
            raise RuntimeError("Browser driver was retired after an uncertain action.")

    def _revoke(self, tab_id: str | None = None) -> None:
        self._generation += 1
        if tab_id is not None and tab_id in self._page_generations:
            self._page_generations[tab_id] += 1

    def _retired(self) -> None:
        self._revoke()
        if self.owned_fixture_urls is not None:
            self._unusable = True

    def _record(self, change: BrowserStateChange) -> None:
        self._revoke(change["tab_id"] if change["type"] == "navigation" else None)
        if self.owned_fixture_urls is not None:
            if self._sequence == 9_007_199_254_740_991:
                self._unusable = True
                raise RuntimeError("Browser event sequence exhausted.")
            self._sequence += 1
            self._changes.append(change)

    def _notice(self, kind: Literal["tab_opened", "tab_closed", "tab_switched", "navigation"], tab_id: str) -> None:
        self._record({"type": kind, "tab_id": tab_id, "sequence": self._sequence + 1})

    async def _dismiss(self, dialog: Dialog, tab_id: str) -> None:
        try:
            kind = dialog.type
            await dialog.dismiss()
            self._record(
                {
                    "type": "dialog_dismissed",
                    "tab_id": tab_id,
                    "sequence": self._sequence + 1,
                    "kind": (
                        # Mypy needs this narrowing; Pyright already narrows the membership check.
                        cast('Literal["alert", "confirm", "prompt", "beforeunload"]', kind)  # pyright: ignore[reportUnnecessaryCast]
                        if kind in ("alert", "confirm", "prompt", "beforeunload")
                        else "other"
                    ),
                }
            )
        except (Error, asyncio.CancelledError):
            # No dismissal was confirmed. Never reopen a retired context.
            await self._retire_from_event()

    async def _download(self, download: Download, tab_id: str) -> None:
        try:
            await download.cancel()
            self._record({"type": "download", "tab_id": tab_id, "sequence": self._sequence + 1, "status": "blocked"})
        except (Error, asyncio.CancelledError):
            await self._retire_from_event()

    async def _join_retirement(self, cancelled: Callable[[], bool] | None = None) -> None:
        assert self._retirement is not None
        retiring = self._retirement
        # Observe even when caller task cancellation interrupts the normal join.
        retiring.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
        if cancelled is None:
            await asyncio.shield(retiring)
            return
        while not retiring.done():
            if cancelled():
                raise BrowserCancelledError()
            await asyncio.wait({retiring}, timeout=0.05)
        if cancelled():
            raise BrowserCancelledError()
        retiring.result()

    async def _retire_from_event(self) -> None:
        self._retired()
        if self._retirement is None:
            self._retirement = asyncio.create_task(self.context.close())
        try:
            await asyncio.shield(self._retirement)
        except (Error, asyncio.CancelledError):
            # Observe close even if this event task is cancelled while it drains.
            self._retirement.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)

    def _refused(self, route: Route) -> None:
        if self.owned_fixture_urls is not None and route.request.is_navigation_request():
            tab_id = None
            try:
                page = route.request.frame.page
                tab_id = next((tid for tid, current in self.tabs.items() if current == page), None)
            except Error:
                # A popup's first navigation can precede its frame. Refusal still applies.
                pass
            self._record(
                {
                    "type": "navigation_refused",
                    "tab_id": tab_id,
                    "sequence": self._sequence + 1,
                    "reason": "policy",
                }
            )

    def page(self, tab_id: str | None) -> tuple[str, Page]:
        self._usable()
        selected = self.active if tab_id is None else tab_id
        page = self.tabs.get(selected)
        if page is None or page.is_closed():
            raise BrowserError("Unknown or closed tab. List the current tabs.")
        if (
            self.owned_fixture_urls is not None
            and page.url != "about:blank"
            and page.url not in self.owned_fixture_urls
        ):
            raise RuntimeError("Owned browser is outside its installed fixture URLs.")
        return selected, page

    def allows(self, url: str) -> bool:
        try:
            return origin(url) in self.allowed_origins
        except (BrowserError, ValueError):
            return False

    async def guard(self, route: Route) -> None:
        try:
            permitted = self.allows(route.request.url) and (
                self.owned_fixture_urls is None or route.request.url in self.owned_fixture_urls
            )
            if not permitted:
                try:
                    self._refused(route)
                finally:
                    await route.abort("blockedbyclient")
                return
            response = await route.fetch(max_redirects=0, timeout=0)
            try:
                if response.status in (301, 302, 303, 307, 308):
                    # The initial URL was allowed. Redirects are unsupported, not policy refusals.
                    # A POST could already have caused an effect; never retry it.
                    await route.abort("failed")
                    return
                await route.fulfill(response=response)
            finally:
                await response.dispose()
        except Error:
            # Transport failures and context close do not prove policy refusal.
            # Keep raw Playwright headers and cookies out of route event errors.
            try:
                await route.abort("failed")
            except Error:
                pass

    async def state(self, *, cancelled: Callable[[], bool] | None = None) -> BrowserState:
        return await self._observation(self._observe_state, cancelled)

    async def _observe_state(self) -> BrowserState:
        self._usable()
        live = {tab_id: page for tab_id, page in self.tabs.items() if not page.is_closed()}
        if self.active not in live:
            self.active = next(reversed(live), "")
        if self.owned_fixture_urls is not None:
            for tab_id in live:
                self.page(tab_id)
            return {
                "tabs": [
                    {
                        "id": tab_id,
                        # Arbitrary page titles can contain private values.
                        "title": "Owned fixture",
                        "url": "about:blank" if page.url == "about:blank" else origin(page.url),
                        "active": tab_id == self.active,
                    }
                    for tab_id, page in live.items()
                ],
                "observation": {
                    "version": 1,
                    "sequence": self._sequence,
                    "dropped_changes": self._sequence - len(self._changes),
                    "title_truncated": False,
                    "changes": [change.copy() for change in self._changes],
                },
            }
        result: BrowserState = {"tabs": []}
        for tab_id, page in live.items():
            captured: str = await page.evaluate("""() => {
                const source = document.title;
                if (typeof source !== 'string') return '';
                let captured = '';
                for (let index = 0; index < source.length && index < 1024; index += 1) {
                    captured += source[index];
                }
                return captured;
            }""")
            title = ""
            for character in captured:
                if 0xD800 <= ord(character) <= 0xDFFF or len((title + character).encode("utf-8")) > 1024:
                    break
                title += character
            result["tabs"].append(
                {"id": tab_id, "title": title, "url": _reported_url(page.url), "active": tab_id == self.active}
            )
        return result

    async def _clear_refs(self, tab_id: str) -> None:
        handles = self._refs[tab_id]
        self._refs[tab_id] = {}
        await self._dispose_refs(list(handles.values()))

    async def _dispose_refs(self, previous: list[tuple[ElementHandle, object, int]]) -> None:
        for handle, binding, _ in previous:
            try:
                await handle.dispose()
                if isinstance(binding, JSHandle):
                    await binding.dispose()
            except Error:
                # The caller may already have closed or navigated the page.
                pass

    def _retire_borrowed_refs(self) -> None:
        if self._retirement is None:
            previous = [entry for handles in self._refs.values() for entry in handles.values()]
            for handles in self._refs.values():
                handles.clear()
            self._retirement = asyncio.create_task(self._dispose_refs(previous))
            self._retirement.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)

    async def invalidate_references(self) -> None:
        """Caller must drain admitted work before handoff and before resuming."""
        self._usable()
        self._revoke()
        generation = self._generation
        for tab_id in self._refs:
            if generation != self._generation:
                break
            await self._clear_refs(tab_id)

    async def navigate(self, action: NavigateInput, *, cancelled: Callable[[], bool] | None = None) -> str:
        tab_id, page = self.page(action["tab_id"])
        history = action["url"] in {"back", "forward", "reload"}
        if history:
            if cancelled and cancelled():
                raise BrowserCancelledError()
            self._revoke()
            await self._observation(lambda: self._clear_refs(tab_id), cancelled)
            navigate_history = {"back": page.go_back, "forward": page.go_forward, "reload": page.reload}[action["url"]]
            await self._guarded_input(
                lambda: self._observation(
                    lambda: navigate_history(wait_until="domcontentloaded", timeout=30_000), cancelled
                ),
                cancelled,
                interruptible=False,
            )
            # Includes same-document history, which may make no network request.
            self.page(tab_id)
            return "History navigation checked."
        if not self.allows(action["url"]) or (
            self.owned_fixture_urls is not None and action["url"] not in self.owned_fixture_urls
        ):
            if self.owned_fixture_urls is not None:
                self._record(
                    {
                        "type": "navigation_refused",
                        "tab_id": tab_id,
                        "sequence": self._sequence + 1,
                        "reason": "policy",
                    }
                )
            raise BrowserError("Navigation is outside the allowed origins.")
        if cancelled and cancelled():
            raise BrowserCancelledError()
        self._revoke()
        await self._observation(lambda: self._clear_refs(tab_id), cancelled)
        await self._guarded_input(
            lambda: self._observation(
                lambda: page.goto(action["url"], wait_until="domcontentloaded", timeout=30_000), cancelled
            ),
            cancelled,
            interruptible=False,
        )
        return "Navigated."

    async def _remote_visible(self, frame: Frame, point: dict[str, float], visited: int) -> tuple[bool, int]:
        assert self.owned_fixture_urls is not None
        child = frame
        while (parent := child.parent_frame) is not None:
            if child.url not in self.owned_fixture_urls or parent.url not in self.owned_fixture_urls:
                return False, visited
            handle = await child.frame_element()
            try:
                checked = await handle.evaluate(_PARENT_VISIBLE, {**point, "visited": visited})
            finally:
                await handle.dispose()
            projected: dict[str, float] | None = checked["point"]
            visited = checked["count"]
            if projected is None:
                return False, visited
            point = projected
            child = parent
        return True, visited

    async def _read_owned(
        self,
        tab_id: str | None,
        *,
        full: bool,
        text_only: bool = False,
        query: str = "",
        deadline: float | None = None,
        scoped: ReadPageScopedInput | None = None,
        wait_generation: int | None = None,
    ) -> BrowserReadV1:
        assert self.owned_fixture_urls is not None
        selected, page = self.page(tab_id)
        root: tuple[ElementHandle, object, int] | None = None
        if scoped is not None and scoped["root"] is not None:
            root = self._refs[selected].get(scoped["root"])
            if root is None or root[2] != self._generation or not isinstance(root[1], dict) or "scope" not in root[1]:
                raise BrowserError("Unknown or expired scope. Read the page again.")
            # Hold this root until after its scan; invalidation disposes every other old ref.
            del self._refs[selected][scoped["root"]]
        report: BrowserReadV1 = {"version": 1, "text": "", "elements": [], "omitted": []}
        if scoped is not None:
            report = BrowserScopedReadV1(**report, scopes=[])

        def omit(
            reason: Literal["frame_limit", "unsupported_root", "work_limit", "text_limit", "report_limit"],
        ) -> None:
            if reason not in report["omitted"]:
                report["omitted"].append(reason)

        visited = 0
        generation = self._generation
        try:
            if not text_only:
                generation += 1
                await self.invalidate_references()
            for index, frame in enumerate(page.frames):
                if scoped is not None and frame != page.main_frame:
                    omit("unsupported_root")
                    continue
                if index == 16:
                    omit("frame_limit")
                    break
                depth, remote = 0, False
                child = frame
                while (parent := child.parent_frame) is not None:
                    depth += 1
                    if child.url not in self.owned_fixture_urls or parent.url not in self.owned_fixture_urls:
                        break
                    if origin(child.url) != origin(parent.url):
                        remote = True
                    child = parent
                if depth > 8 or child != page.main_frame or frame.url not in self.owned_fixture_urls:
                    omit("frame_limit" if depth > 8 else "unsupported_root")
                    continue
                if visited >= 2000:
                    omit("work_limit")
                    break
                request = {
                    "action": "scan",
                    "report": report,
                    "visited": visited,
                    "depth": depth,
                    "full": full,
                    "textOnly": text_only and not remote,
                    "query": " ".join(query.split()).lower(),
                    "remote": remote,
                    "publicValues": self.public_values,
                    "nonce": self._nonce,
                    "nextRef": self._next_ref,
                }
                if scoped is not None:
                    request.update(
                        {
                            "domDepth": scoped["depth"],
                            "scopeRoot": root is not None,
                            "expected": {"label": cast(dict[str, str], root[1])["scope"]} if root else None,
                        }
                    )
                if root is not None:
                    scan = await root[0].evaluate_handle(_OWNED_ELEMENT, request)
                else:
                    scan = await frame.locator("html").evaluate_handle(
                        _OWNED_ELEMENT,
                        request,
                        timeout=None if deadline is None else max(1, (deadline - time.monotonic()) * 1000),
                    )
                try:
                    extracted = await scan.evaluate("({report, visited}) => ({report, visited})")
                    report = cast(BrowserReadV1, extracted["report"])
                    visited = extracted["visited"]
                    candidates = await scan.get_property("targets")
                    try:
                        properties = await candidates.get_properties()
                        for candidate in properties.values():
                            try:
                                value = await candidate.evaluate("({item, x, y, scope}) => ({item, x, y, scope})")
                                if remote:
                                    visible, visited = await self._remote_visible(
                                        frame, {"x": value["x"], "y": value["y"]}, visited
                                    )
                                    if visited >= 2000:
                                        omit("work_limit")
                                    if visible:
                                        item = value["item"]
                                        summary = " ".join(
                                            [
                                                "Read only: remote frame",
                                                item["role"],
                                                item["label"],
                                                *([item["value"]] if "value" in item else []),
                                                *(option["label"] for option in item.get("options", [])),
                                            ]
                                        )
                                        text = " ".join(part for part in (report["text"], summary) if part)
                                        # Reserve every possible omission: later frame checks can add codes.
                                        proposed = {
                                            **report,
                                            "text": text,
                                            "omitted": [
                                                "report_limit",
                                                "text_limit",
                                                "target_limit",
                                                "work_limit",
                                                "frame_limit",
                                                "unsupported_root",
                                                "unsupported_control",
                                                "remote_action",
                                                "private",
                                                "value",
                                                "name_limit",
                                            ],
                                        }
                                        if len(text.encode("utf-8")) > 16384:
                                            omit("text_limit")
                                        elif (
                                            len(
                                                json.dumps(proposed, ensure_ascii=False, separators=(",", ":")).encode(
                                                    "utf-8"
                                                )
                                            )
                                            > 65536
                                        ):
                                            omit("report_limit")
                                        else:
                                            report["text"] = text
                                    else:
                                        omit("unsupported_root")
                                else:
                                    handle = (await candidate.get_property("node")).as_element()
                                    if handle is None:
                                        raise BrowserError("Owned read lost an element. Read again.")
                                    held_observation = (
                                        {"scope": value["item"]["label"]}
                                        if value.get("scope") is True
                                        else await candidate.get_property("observation")
                                    )
                                    if self._unusable or generation != self._generation or page.is_closed():
                                        await handle.dispose()
                                        if isinstance(held_observation, JSHandle):
                                            await held_observation.dispose()
                                        raise BrowserError("Page changed while reading. Read the page again.")
                                    self._next_ref += 1
                                    self._refs[selected][value["item"]["ref"]] = (handle, held_observation, generation)
                            finally:
                                await candidate.dispose()
                    finally:
                        await candidates.dispose()
                finally:
                    await scan.dispose()
            if (
                self._unusable
                or (
                    generation != self._generation
                    if not text_only or wait_generation is None
                    else wait_generation != self._page_generations.get(selected)
                )
                or self.tabs.get(selected) is not page
                or page.is_closed()
            ):
                raise BrowserError("Page changed while reading. Read the page again.")
            return report
        except BaseException as exc:
            if not text_only and not self._unusable and generation == self._generation:
                await self.invalidate_references()
            if scoped is not None and isinstance(exc, Exception):
                raise BrowserError("Scope is stale, hidden or unsupported. Read the page again.") from None
            raise
        finally:
            if root is not None:
                await root[0].dispose()

    @property
    def read_page_scoped(self) -> Callable[..., Awaitable[BrowserScopedReadV1]] | None:
        return self._read_page_scoped if self.owned_fixture_urls is not None else None

    async def _read_page_scoped(
        self, action: ReadPageScopedInput, *, cancelled: Callable[[], bool] | None = None
    ) -> BrowserScopedReadV1:
        return cast(
            BrowserScopedReadV1,
            await self._observation(
                lambda: self._read_owned(action["tab_id"], full=action["filter"] == "all", scoped=action), cancelled
            ),
        )

    async def _read_borrowed(
        self, tab_id: str | None, *, full: bool, text_only: bool = False, query: str = "", finding: bool = False
    ) -> BrowserReadV1:
        selected, page = self.page(tab_id)
        generation = self._generation
        if not text_only:
            generation += 1
            await self.invalidate_references()
        self._usable()
        scan = await page.evaluate_handle(
            _BORROWED_READ,
            {"nonce": self._nonce, "nextRef": self._next_ref, "full": full, "textOnly": text_only, "finding": finding},
        )
        try:
            report_handle = await scan.get_property("report")
            try:
                encoded = await report_handle.json_value()
                if not isinstance(encoded, str):
                    raise BrowserError("Browser read exceeds the supported report budget.")
                report = cast(BrowserReadV1, json.loads(encoded))
            finally:
                await report_handle.dispose()
            if (
                not isinstance(cast("object", report["text"]), str)
                or len(report["text"].encode("utf-8")) > 16_384
                or len(json.dumps(report, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) > 65_536
            ):
                raise BrowserError("Browser read exceeds the supported report budget.")
            # Match ECMAScript trim, including its BOM and excluding Python-only whitespace.
            report["text"] = report["text"].strip(
                "\u0009\u000a\u000b\u000c\u000d\u0020\u00a0\u1680"
                "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a"
                "\u2028\u2029\u202f\u205f\u3000\ufeff"
            )
            if query:
                report["elements"] = [
                    item for item in report["elements"] if query in " ".join(item["label"].split()).casefold()
                ]
            if len(report["elements"]) > 100:
                report["elements"] = report["elements"][:100]
                if "target_limit" not in report["omitted"]:
                    report["omitted"].append("target_limit")
            returned = {item["ref"]: item for item in report["elements"]}
            counter = await scan.get_property("nextRef")
            try:
                observed_next = cast(int, await counter.json_value())
            finally:
                await counter.dispose()
            targets = await scan.get_property("targets")
            try:
                for candidate in (await targets.get_properties()).values():
                    try:
                        item_handle = await candidate.get_property("item")
                        try:
                            ref = await item_handle.evaluate(
                                """(item) => {
                                  const { ref } = item;
                                  return typeof ref === 'string' && ref.length <= 65536 ? ref : null;
                                }"""
                            )
                        finally:
                            await item_handle.dispose()
                        published = returned.get(ref)
                        if published is None:
                            continue
                        binding_handle = await candidate.get_property("binding")
                        try:
                            observed = await binding_handle.json_value()
                            binding = _serialize_binding(observed)
                            if binding != _serialize_binding(observed, published):
                                raise BrowserError("Page changed while reading. Read the page again.")
                        finally:
                            await binding_handle.dispose()
                        node = await candidate.get_property("node")
                        handle = node.as_element()
                        if handle is None:
                            await node.dispose()
                            raise BrowserError("Page changed while reading. Read the page again.")
                        try:
                            await _check_borrowed_input(handle)
                            if self._unusable or generation != self._generation or page.is_closed():
                                raise BrowserError("Page changed while reading. Read the page again.")
                        except BaseException:
                            await handle.dispose()
                            raise
                        self._refs[selected][published["ref"]] = (handle, binding, generation)
                    finally:
                        await candidate.dispose()
            finally:
                await targets.dispose()
            if self._unusable or generation != self._generation or page.is_closed():
                raise BrowserError("Page changed while reading. Read the page again.")
            if not text_only:
                self._next_ref = observed_next
            return report
        except BaseException:
            if not text_only and not self._unusable and generation == self._generation:
                await self.invalidate_references()
            raise
        finally:
            await scan.dispose()

    async def _observation(
        self,
        work: Callable[[], Awaitable[_Observation]],
        cancelled: Callable[[], bool] | None,
        *,
        timeout: float | None = None,
    ) -> _Observation:
        if cancelled is not None and cancelled():
            raise BrowserCancelledError()

        async def observe() -> _Observation:
            return await work()

        reading = asyncio.create_task(observe())
        deadline = None if timeout is None else time.monotonic() + timeout
        retired = False
        try:
            if cancelled is None and deadline is None:
                return await asyncio.shield(reading)
            while not reading.done():
                if cancelled is not None and cancelled():
                    raise BrowserCancelledError()
                if deadline is not None and time.monotonic() >= deadline:
                    retired = True
                    raise BrowserError("Browser observation timed out.")
                await asyncio.wait({reading}, timeout=0.05)
            if cancelled is not None and cancelled():
                raise BrowserCancelledError()
            return reading.result()
        except (BrowserCancelledError, asyncio.CancelledError):
            retired = True
            raise
        finally:
            if retired:
                # Clear admission synchronously; the caller still owns its context.
                self._unusable = True
                self._revoke()
                # Do not block Stop on a renderer, but always observe late rejection.
                reading.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
                if self.owned_fixture_urls is not None:
                    for handles in self._refs.values():
                        handles.clear()
                    if self._retirement is None:
                        self._retirement = asyncio.create_task(self.context.close())
                    self._retirement.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
                else:
                    self._retire_borrowed_refs()

    async def read_page(
        self, action: ReadPageInput, *, cancelled: Callable[[], bool] | None = None
    ) -> str | BrowserReadV1:
        if self.owned_fixture_urls is not None:
            return await self._observation(
                lambda: self._read_owned(action["tab_id"], full=action["filter"] == "all"), cancelled
            )
        return await self._observation(
            lambda: self._read_borrowed(action["tab_id"], full=action["filter"] == "all"), cancelled, timeout=5
        )

    async def get_page_text(
        self, action: TabInput, *, cancelled: Callable[[], bool] | None = None
    ) -> str | BrowserReadV1:
        if self.owned_fixture_urls is not None:
            return await self._observation(
                lambda: self._read_owned(action["tab_id"], full=True, text_only=True), cancelled
            )
        report = await self._observation(
            lambda: self._read_borrowed(action["tab_id"], full=True, text_only=True), cancelled, timeout=5
        )
        return report["text"]

    async def find(self, action: FindInput, *, cancelled: Callable[[], bool] | None = None) -> str | BrowserReadV1:
        if self.owned_fixture_urls is not None:
            return await self._observation(
                lambda: self._read_owned(action["tab_id"], full=False, query=action["query"]), cancelled
            )
        return await self._observation(
            lambda: self._read_borrowed(
                action["tab_id"], full=False, query=" ".join(action["query"].split()).casefold(), finding=True
            ),
            cancelled,
            timeout=5,
        )

    async def _target(
        self, target: str, tab_id: str | None, *, cancelled: Callable[[], bool] | None = None
    ) -> ElementHandle:
        return await self._observation(lambda: self._checked_target(target, tab_id), cancelled, timeout=5)

    @asynccontextmanager
    async def _reference_action(self) -> AsyncGenerator[None, None]:
        self._usable()
        if self._reference_action_active:
            raise BrowserError("A reference action is already active on this driver.")
        self._reference_action_active = True
        try:
            yield
        finally:
            self._reference_action_active = False

    async def _checked_target(self, target: str, tab_id: str | None) -> ElementHandle:
        selected, page = self.page(tab_id)
        ref = self._refs[selected].get(target)
        if ref is None or ref[2] != self._generation:
            raise BrowserError("Unknown or stale element reference. Read the page again.")
        handle, binding, _ = ref
        try:
            if self.owned_fixture_urls is not None:
                await self._describe_target({"target": target, "tab_id": selected})
                return handle
            await _check_borrowed_input(handle)
            observed = await page.evaluate(
                _BORROWED_READ,
                {
                    "nonce": self._nonce,
                    "nextRef": self._next_ref,
                    "full": False,
                    "textOnly": False,
                    "checkedNode": handle,
                },
            )
            if (
                _serialize_binding(observed) != binding
                or ref[2] != self._generation
                or self._refs[selected].get(target) is not ref
            ):
                raise BrowserError("Stale element reference. Read the page again.")
        except Exception as exc:
            self._refs[selected].pop(target, None)
            await handle.dispose()
            raise BrowserError("Stale element reference. Read the page again.") from exc
        return handle

    async def _guarded_input(
        self,
        work: Callable[[], Awaitable[object]],
        cancelled: Callable[[], bool] | None,
        *,
        interruptible: bool = True,
    ) -> None:
        if cancelled and cancelled():
            raise BrowserCancelledError()
        try:
            if self.owned_fixture_urls is None and interruptible:
                await self._observation(work, cancelled)
            else:
                await work()
            if cancelled and cancelled():
                raise BrowserCancelledError()
        except BaseException as error:
            if not self._unusable:
                self._unusable = True
                self._revoke()
            if self.owned_fixture_urls is not None:
                try:
                    if self._retirement is None:
                        self._retirement = asyncio.create_task(self.context.close())
                    if isinstance(error, (asyncio.CancelledError, BrowserCancelledError)):
                        self._retirement.add_done_callback(
                            lambda done: done.exception() if not done.cancelled() else None
                        )
                    else:
                        await self._join_retirement(cancelled)
                except Exception:
                    pass
                if isinstance(error, (asyncio.CancelledError, BrowserCancelledError)):
                    raise
                raise BrowserError("Owned browser action outcome is unknown; context retired.") from None
            self._retire_borrowed_refs()
            if isinstance(error, (asyncio.CancelledError, BrowserCancelledError)):
                raise
            raise BrowserError("Borrowed browser input outcome is unknown; driver retired.") from None

    async def click(self, action: ClickInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        if self.owned_fixture_urls is not None:
            await self._owned_action(action["tab_id"], action["target"], {"action": "click"}, cancelled=cancelled)
            return
        async with self._reference_action():
            selected, _ = self.page(action["tab_id"])
            handle = await self._target(action["target"], action["tab_id"], cancelled=cancelled)

            async def click_and_dispose() -> None:
                if cancelled and cancelled():
                    raise BrowserCancelledError()
                self._refs[selected].pop(action["target"], None)
                try:
                    await handle.click(timeout=3000)
                finally:
                    try:
                        await handle.dispose()
                    except Error:
                        # A closed page or navigation can already have released this remote object.
                        pass

            await self._guarded_input(click_and_dispose, cancelled)

    @property
    def describe_target(self) -> Callable[..., Awaitable[dict[str, str]]] | None:
        return self._describe_target if self.owned_fixture_urls is not None else None

    async def _describe_target(
        self, action: ClickInput, *, cancelled: Callable[[], bool] | None = None
    ) -> dict[str, str]:
        return await self._observation(lambda: self._checked_description(action), cancelled)

    async def _checked_description(self, action: ClickInput) -> dict[str, str]:
        selected, page = self.page(action["tab_id"])
        ref = self._refs[selected].get(action["target"])
        if ref is None or ref[2] != self._generation or isinstance(ref[1], dict):
            raise BrowserError("Element reference is stale or not ready. Read the page again.")
        handle, binding, _ = ref
        try:
            description: object = await handle.evaluate(_OWNED_ACT, {"binding": binding, "action": "describe"})
        except Exception as exc:
            raise BrowserError("Stale element reference. Read the page again.") from exc
        if (
            not isinstance(description, dict)
            or ref[2] != self._generation
            or self._refs[selected].get(action["target"]) is not ref
            or self.page(selected)[1] is not page
        ):
            raise BrowserError("Element reference changed. Read the page again.")
        return cast(dict[str, str], description)

    async def type(self, action: TypeInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        if self.owned_fixture_urls is not None:
            await self._owned_action(
                action["tab_id"], action["target"], {"action": "type", "text": action["text"]}, cancelled=cancelled
            )
            return
        if action["target"] is not None:
            async with self._reference_action():
                handle = await self._target(action["target"], action["tab_id"], cancelled=cancelled)
                await self._guarded_input(lambda: handle.fill(action["text"]), cancelled)
        else:
            _, page = self.page(action["tab_id"])
            await self._guarded_input(lambda: page.keyboard.insert_text(action["text"]), cancelled)

    @property
    def key(self) -> Callable[[KeyInput], Awaitable[None]] | None:
        return self._key if self.owned_fixture_urls is None else None

    async def _key(self, action: KeyInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        _, page = self.page(action["tab_id"])
        # Accept documented Playwright key names; the model cannot evaluate code.
        await self._guarded_input(lambda: page.keyboard.press("+".join(action["keys"])), cancelled)

    @property
    def scroll(self) -> Callable[[ScrollInput], Awaitable[None]] | None:
        return self._scroll if self.owned_fixture_urls is None else None

    async def _scroll(self, action: ScrollInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        _, page = self.page(action["tab_id"])
        amount = action["amount"]
        if amount > 3072:
            raise BrowserError("This example allows at most four viewports per scroll.")
        x = amount * (-1 if action["direction"] == "left" else 1) if action["direction"] in {"left", "right"} else 0
        y = amount * (-1 if action["direction"] == "up" else 1) if action["direction"] in {"up", "down"} else 0
        await self._guarded_input(lambda: page.mouse.wheel(x, y), cancelled)

    @property
    def scroll_to(self) -> Callable[[ClickInput], Awaitable[None]] | None:
        # Generic refs lack the owned immutable-record and same-task checks.
        return self._scroll_to if self.owned_fixture_urls is not None else None

    async def _scroll_to(self, action: ClickInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        await self._owned_action(action["tab_id"], action["target"], {"action": "scroll_to"}, cancelled=cancelled)
        await self._observation(self.invalidate_references, cancelled)

    @property
    def wait_for(self) -> Callable[..., Awaitable[str]] | None:
        # Generic text is not the bounded safe V1 read required by this member.
        return self._wait_for if self.owned_fixture_urls is not None else None

    async def _wait_for(self, action: WaitForInput, *, cancelled: Callable[[], bool] | None = None) -> str:
        selected, page = self.page(action["tab_id"])
        generation, active = self._generation, self.active
        wait_generation = None if action["tab_id"] is None else self._page_generations[selected]
        deadline = time.monotonic() + action["timeout_ms"] / 1000
        text = " ".join(action["text"].split()).lower()
        while True:
            if cancelled is not None and cancelled():
                raise BrowserCancelledError("Browser execution was cancelled.")
            if (
                self._generation != generation or self.active != active
                if wait_generation is None
                else wait_generation != self._page_generations.get(selected)
            ) or self.page(selected)[1] is not page:
                raise BrowserError("Page changed while waiting. Read the page again.")
            if time.monotonic() >= deadline:
                raise BrowserError("Visible condition timed out.")
            read_started = time.monotonic()
            reading = asyncio.create_task(
                self._read_owned(
                    selected, full=True, text_only=True, deadline=deadline, wait_generation=wait_generation
                )
            )
            try:
                while not reading.done():
                    if cancelled is not None and cancelled():
                        raise BrowserCancelledError("Browser execution was cancelled.")
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise BrowserError("Visible condition timed out.")
                    await asyncio.wait({reading}, timeout=min(0.05, remaining))
                report = reading.result()
            except PlaywrightTimeoutError:
                raise BrowserError("Visible condition timed out.") from None
            finally:
                if not reading.done():
                    self._unusable = True
                    self._revoke()
                    reading.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
                    # wait_for exists only on owned fixtures. Retain cleanup without delaying Stop.
                    if self._retirement is None:
                        self._retirement = asyncio.create_task(self.context.close())
                    self._retirement.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
            if cancelled is not None and cancelled():
                raise BrowserCancelledError("Browser execution was cancelled.")
            if (
                self._generation != generation or self.active != active
                if wait_generation is None
                else wait_generation != self._page_generations.get(selected)
            ) or self.page(selected)[1] is not page:
                raise BrowserError("Page changed while waiting. Read the page again.")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise BrowserError("Visible condition timed out.")
            if text in " ".join(report["text"].split()).lower():
                return "Visible condition met."
            # Do not start another read if even the previous observation's
            # duration cannot fit after the next poll interval.
            next_read_fits = remaining > 0.1 + (time.monotonic() - read_started)
            await asyncio.sleep(0.1 if next_read_fits else remaining)

    async def select_option(self, action: SelectOptionInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        if self.owned_fixture_urls is not None:
            await self._owned_action(
                action["tab_id"],
                action["target"],
                {"action": "select_option", "values": action["values"]},
                cancelled=cancelled,
            )
            return
        supplied = cast("object", action["values"])
        if not isinstance(supplied, list):
            raise BrowserError("Option values must be a list of strings.")
        selected = list(cast("list[object]", supplied))
        if any(not isinstance(value, str) for value in selected):
            raise BrowserError("Option values must be a list of strings.")
        async with self._reference_action():
            handle = await self._target(action["target"], action["tab_id"], cancelled=cancelled)
            await self._guarded_input(lambda: handle.select_option(cast("list[str]", selected)), cancelled)

    @property
    def set_checked(self) -> Callable[..., Awaitable[None]] | None:
        return self._set_checked if self.owned_fixture_urls is not None else None

    async def _set_checked(self, action: dict[str, object], *, cancelled: Callable[[], bool] | None = None) -> None:
        await self._owned_action(
            cast("str | None", action["tab_id"]),
            cast(str, action["target"]),
            {"action": "set_checked", "checked": action["checked"]},
            cancelled=cancelled,
        )

    @property
    def hover(self) -> Callable[[ClickInput], Awaitable[None]] | None:
        return self._hover if self.owned_fixture_urls is None else None

    async def _hover(self, action: ClickInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        async with self._reference_action():
            handle = await self._target(action["target"], action["tab_id"], cancelled=cancelled)
            await self._guarded_input(lambda: handle.hover(), cancelled)

    async def _owned_action(
        self,
        tab_id: str | None,
        target: str | None,
        args: dict[str, object],
        *,
        cancelled: Callable[[], bool] | None = None,
    ) -> None:
        async with self._reference_action():
            if cancelled is not None and cancelled():
                raise BrowserCancelledError("Browser execution was cancelled.")
            selected, _ = self.page(tab_id)
            ref = self._refs[selected].get(target) if target is not None else None
            if ref is None or ref[2] != self._generation or isinstance(ref[1], dict):
                raise BrowserError("Element reference is stale or not ready. Read the page again.")
            handle, binding, _ = ref
            try:
                result = await self._observation(
                    lambda: handle.evaluate(_OWNED_ACT, {"binding": binding, **args}), cancelled
                )
                if cancelled is not None and cancelled():
                    raise BrowserCancelledError("Browser execution was cancelled.")
                if result is not True and result is not False and result != "invalid_native_date":
                    raise RuntimeError("Owned action did not return a checked result.")
            except BaseException as error:
                # No checked pre-action reply: an effect may already have happened.
                # Revoke use before close, which may itself stall or fail.
                if not self._unusable:
                    self._unusable = True
                    self._revoke()
                    if self._retirement is None:
                        self._retirement = asyncio.create_task(self.context.close())
                    if isinstance(error, (asyncio.CancelledError, BrowserCancelledError)):
                        self._retirement.add_done_callback(
                            lambda done: done.exception() if not done.cancelled() else None
                        )
                    else:
                        await self._join_retirement(cancelled)
                raise
            if result == "invalid_native_date":
                raise BrowserError("Use a valid native date in YYYY-MM-DD format.")
            if result is False:
                raise BrowserError("Element reference is stale or not ready. Read the page again.")

    async def screenshot(
        self, action: TabInput, *, cancelled: Callable[[], bool] | None = None
    ) -> ResponseInputImageContentParam:
        if self.owned_fixture_urls is not None:
            return await self._pointer.browser_capture(action["tab_id"], None, cancelled=cancelled)
        png = await self._observation(
            lambda: self.page(action["tab_id"])[1].screenshot(type="png", full_page=False), cancelled
        )
        return {"type": "input_image", "image_url": "data:image/png;base64," + base64.b64encode(png).decode()}

    @property
    def zoom(self) -> Callable[[ZoomInput], Awaitable[ResponseInputImageContentParam]] | None:
        return self._zoom if self.public_viewports else None

    async def _zoom(
        self, action: ZoomInput, *, cancelled: Callable[[], bool] | None = None
    ) -> ResponseInputImageContentParam:
        return await self._pointer.browser_capture(action["tab_id"], action["region"], cancelled=cancelled)

    async def owned_computer(self, record: ElementHandle, *, cancelled: Callable[[], bool]) -> OwnedComputer:
        return await self._pointer.create(record, cancelled)

    async def owned_browser(
        self, record: ElementHandle, *, cancelled: Callable[[], bool], canvases: list[ElementHandle] | None = None
    ) -> OwnedBrowser:
        return await self._pointer.create_browser(record, cancelled, canvases)

    async def new_tab(self, action: NewTabInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        self._usable()
        if action["url"] is not None and (
            not self.allows(action["url"])
            or (self.owned_fixture_urls is not None and action["url"] not in self.owned_fixture_urls)
        ):
            if self.owned_fixture_urls is not None:
                self._record(
                    {
                        "type": "navigation_refused",
                        "tab_id": None,
                        "sequence": self._sequence + 1,
                        "reason": "policy",
                    }
                )
            raise BrowserError("Navigation is outside the allowed origins.")
        if cancelled and cancelled():
            raise BrowserCancelledError()

        created: Page | None = None
        closing: asyncio.Task[None] | None = None

        def close_created() -> asyncio.Task[None] | None:
            nonlocal closing
            if self.owned_fixture_urls is None and created is not None and closing is None:
                closing = asyncio.create_task(created.close())
                closing.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
            return closing

        async def open_page() -> None:
            nonlocal created
            completed = False
            try:
                created = await self.context.new_page()
                if cancelled and cancelled():
                    raise BrowserCancelledError()
                self._usable()
                self._register(created)
                if action["url"] is not None:
                    await created.goto(action["url"], wait_until="domcontentloaded")
                if cancelled and cancelled():
                    raise BrowserCancelledError()
                self._usable()
                completed = True
            finally:
                if not completed and (drain := close_created()) is not None:
                    try:
                        await asyncio.shield(drain)
                    except Error:
                        pass

        # The observed late task owns its page even after Stop releases this await.
        try:
            await self._guarded_input(lambda: self._observation(open_page, cancelled), cancelled, interruptible=False)
        except BaseException as error:
            drain = close_created()
            if drain is not None and not isinstance(error, (asyncio.CancelledError, BrowserCancelledError)):
                try:
                    await asyncio.shield(drain)
                except Error:
                    pass
            raise

    async def switch_tab(self, action: TabInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        tab_id, page = self.page(action["tab_id"])
        await self._observation(self.invalidate_references, cancelled)
        await self._observation(
            lambda: self._guarded_input(page.bring_to_front, cancelled, interruptible=False), cancelled
        )
        self.active = tab_id
        self._notice("tab_switched", tab_id)

    async def close_tab(self, action: TabInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        tab_id, page = self.page(action["tab_id"])
        await self._observation(lambda: self._clear_refs(tab_id), cancelled)
        await self._observation(lambda: self._guarded_input(page.close, cancelled, interruptible=False), cancelled)


@asynccontextmanager
async def open_browser(
    url: str,
    *,
    headless: bool = True,
    handle_sigint: bool = True,
    owned_fixture_urls: frozenset[str] | None = None,
    public_values: frozenset[tuple[str, str, str]] = frozenset(),
    public_viewports: frozenset[str] = frozenset(),
    context_setup: Callable[[BrowserContext], Awaitable[None]] | None = None,
    setup_stopped: asyncio.Event | None = None,
) -> AsyncGenerator[PlaywrightBrowser]:
    channel = example_browser_channel()
    allowed = {origin(url), *(origin(installed) for installed in owned_fixture_urls or ())}
    async with async_playwright() as playwright:
        if setup_stopped is not None and setup_stopped.is_set():
            raise BrowserCancelledError("Browser setup was stopped.")
        browser = await playwright.chromium.launch(
            headless=headless,
            channel=channel,
            chromium_sandbox=True,
            handle_sigint=handle_sigint,
            timeout=15_000,
            env={
                name: value
                for name in (
                    "PATH",
                    "HOME",
                    "TMPDIR",
                    *(
                        ("DISPLAY", "WAYLAND_DISPLAY", "XAUTHORITY", "XDG_RUNTIME_DIR")
                        if not headless and sys.platform == "linux"
                        else ()
                    ),
                )
                if (value := os.environ.get(name)) is not None
            },
        )
        try:
            if setup_stopped is not None and setup_stopped.is_set():
                raise BrowserCancelledError("Browser setup was stopped.")

            async def retire_setup() -> None:
                assert setup_stopped is not None
                await setup_stopped.wait()
                await browser.close()

            retirement = asyncio.create_task(retire_setup()) if setup_stopped is not None else None
            try:
                context = await browser.new_context(
                    viewport={"width": 1024, "height": 768},
                    accept_downloads=False,
                    service_workers="block",
                )
                if setup_stopped is not None and setup_stopped.is_set():
                    raise BrowserCancelledError("Browser setup was stopped.")
                if context_setup is not None:
                    await context_setup(context)
                driver = PlaywrightBrowser(
                    context,
                    allowed,
                    owned_fixture_urls=owned_fixture_urls,
                    public_values=public_values,
                    public_viewports=public_viewports,
                )
                await context.route("**/*", driver.guard)

                async def refuse_socket(route: WebSocketRoute) -> None:
                    await route.close()

                await context.route_web_socket("**/*", refuse_socket)
                await driver.new_tab({"url": url})
                if setup_stopped is not None and setup_stopped.is_set():
                    raise BrowserCancelledError("Browser setup was stopped.")
            finally:
                if retirement is not None:
                    assert setup_stopped is not None
                    if not setup_stopped.is_set():
                        retirement.cancel()
                    await asyncio.gather(retirement, return_exceptions=True)
            if setup_stopped is not None and setup_stopped.is_set():
                raise BrowserCancelledError("Browser setup was stopped.")
            yield driver
        finally:
            await browser.close()
