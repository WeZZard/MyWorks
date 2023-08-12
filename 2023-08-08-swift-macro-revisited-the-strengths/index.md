---
title: "Swift Macro: Revisited - The Strengths"
category: Programming
tags: [Swift, Macro]
isPublished: false
---

From the sessions at WWDC 2023, we've learned that Swift Macro aims to:

- Eliminate boilerplates
- Make tedious things easy
- Share with other developers in packages

However, these goals are not exclusive to Swift Macro; they are common
targets for most common language features in Swift such as function, type
and module. One could argue that all high-level programming languages
aspire to these ends. There must be something else that Swift Macro excels
at; otherwise, it would be redundant.

So, what is it that Swift Macro does exceptionally well?

Understanding the unique strengths of Swift Macro is crucial. It will
guide us in crafting Swift macros that are effective, inform us of the
boundaries when creating them, and ultimately lead us to produce
well-designed Swift macros. This understanding is the essence of Swift
Macro.

To grasp this, we must first comprehend the problems that existing Swift
language features, such as functions, types, and modules, have managed to
solve and their limitations. The key to understanding what set Swift
Macro apart lies in this exploration.

## What Existing Code Reuse Methods Managed To Solve?

### Functions

"Function" is ubiquitous in high-level programming languages. While they
might be called subroutines, routines, subprograms, or procedures in
different languages, their core purpose remains consistent: providing
reusable units of execution. This has remained unchanged since the concept
of function was initially brought to high-level programming languages by
FORTRAN with the name "subroutine".

TODO: An example of the FORTRAN subroutine.

But the "function" in FORTRAN, known as a subroutine, has significant room
for improvement. As programming evolved, programmers then found that code
could be better understood if:

- Variables are only accessible within the block of a control structure
  like the `IF` statement or loop.
- Control structures could be more expressive like using
  `IF-THEN-ELSE-END` instead of a simple `IF` statement.
- The `GOTO` statement could be eliminated by more advanced control
  structures.
- The "function" could be defined within other "functions".

All these points above comprised the concept of structured programming, a
significant movement in computer science. ALGOL 60, a pioneer in this
movement, adopted these principles at a very early stage.

TODO: An example of ALGOL 60's structured programming

Nowadays, these principles are foundational in Swift functions.

### Types

The adoption of structured programming made programs more comprehensible,
paving the way for more developers to join the field. As software
development evolved to tackle more complex problems, the traditional
methods of organizing code — primarily through functions, files, and
directories — became limiting. While functions allowed for a granular
level of logic encapsulation, and files/directories provided a means to
group related code, there was a growing need for more sophisticated
mechanisms to manage and reuse code at different levels of granularity.

Simula, encoded designing for simulating real-world processes in its name,
introduced the concept of object-oriented programming, allowing developers
to create types with variables and functions as members. These members
were accessed via dot notations and were scoped within the type.
Additionally, one type could inherit from another, further enhancing code
reusability.

TODO: Figure: dot notation and type inheritance

These practices were then popularized by Smalltalk and later C++ and are
currently upheld by Swift types.

### Modules

Yet, challenges still lay ahead for programmers. How to reuse code between
projects? Copy and paste? How to accelerate compilation by avoiding the
commonly reused code? Buy more powerful machines? Modula-2 introduced the
concept of modules to address these issues, keeping developers away from
tedious pushes on keyboards and money talks.

Modules introduced by Modula-2 enabled the encapsulation of code at a
granularity greater than that of types, being more convenient than files
and directories. More than that, this feature also brought separate
compilation and segregation between interfaces and implementations which
bring faster build speed and better software design. These advantages now
emerged in Swift modules.

TODO: Figure: module-level code reuse and lexical scope

By tracing the evolution of code reuse, we can find that people tend to
create concepts that aggregate the smaller ones using a protective
mechanism. Here is the summary:

- Functions aggregate execution flows and variables and protect them
  with control structures and lexical scopes;
- Types aggregate variables and functions and protect them with
  instance name or type name;
- Modules aggregate variables, types and functions and protect them
  with the module's namespaces;

TODO: Figure: protection hierarchy of modules/types/functions

All these properties help us keep the code easy to understand as the code
size increases. These code reuse methods also built the existing hierarchy
of encapsulation in Swift.

However, what gives them advantages also caps their capabilities. Due to
the protective mechanisms over the encapsulation hierarchy, there are
still programming concepts that cannot be encapsulated -- because some
concepts are requiring us to drop this protection. Plus, none of these
code reuse methods can receive the programmer's source code as input --
they can only receive data or closures.

Now, we no longer can expand the types of encapsulate-able programming
concepts by merely following the established trends of existing code reuse
methods.

## What Swift Macros Do Exceptionally Well?

But Swift Macro enables encapsulation over many of them by adopting
different design philosophies. To help you build a comprehensive
understanding of these design philosophies, I would like to show you the
nature of Swift Macro with some typical examples.

### Compile-Time Checked Literals

Since design software like Figma and Sketch represent the RGB color with 6
hexadecimal digits. Developers often extend the type of color to allow
direct copying and pasting of RGB values from design software for use in
Swift:

```swift
import SwiftUI

// Color extension
extension Color {

  public init(_ hex: UInt)

}

// Use example
Color(0xFFEEAA)
```

But how can one ensure the pasted value represents a valid RGB color?
Since we are copying and pasting, the digits themselves could be shorter
than what it was in the original place.

```swift
// Invalid color.
Color(0xFFEEA)
```

With Swift macro, these "literals" could be checked at compile-time:

TODO: Replace it with a diagram

```swift
#Color(0xFFEEAA) // compiled
#Color(0xFFEEA) // invalid, not compiled
```

In this example, we can know that we can do compile-time checking with
Swift macros.

### Code Style

In practice, we often want to avoid explicitly unwrapping optional values
with an exclamation mark:

```swift
func foo(_ bar: Int?) {
  print(bar!)
}
```

Instead, they prefer a safer approach using `guard let ... else`:

```swift
func foo(_ bar: Int?) {
  guard let bar else {
    return
  }
  print(bar)
}
```

However, this can be cumbersome, especially with multiple optional
parameters.

Given the nature of programming, there might be a desire to encapsulate
this safe unwrapping process for reuse. Unfortunately, since a function
protects its internal execution flow from inner functions' return for the
sake of structured programming, we cannot encapsulate this
`guard let ... else` in a function -- because the `return` statement in a
function cannot make the caller site function exit.

```swift
func guard<T>(_ value: T?) -> T {
  guard let value else {
    // This return cannot help `foo` to exit.
    // More than that, this function does not compile.
    return
  }
  return value
}

func foo(_ bar: Int?) {
  let bar = guard(bar)
  print(bar)
}
```

But Swift Macro offers a viable way of such kind of encapsulation. We can
have a macro called `#unwrapped` which is used as the code shown below:

```swift
func foo(_ bar: Int?) {
  #unwrapeped(bar) {
    print(bar)
  }
}
```

This could be expanded as:

```swift
func foo(_ bar: Int?) {
  // #unwrapped expansion began
  guard let bar = bar else {
    return
  }
  print(bar)
  // #unwrapped expansion ended
}
```

Then the control flow of the `foo` function could be affected by the
`#unwrapped` macro now. More than that, the variable `bar` received by the
`print` function is the one declared by the `guard let bar` statement --
which is also brought by the expansion of the `#unwrapped` macro. This
example shows the evidence that the expansion of a freestanding Swift
macro could **involve control flow manipulation** and
**lexical scope sharing**.

### Extending Type's Behavior

The capabilities of Swift Macro are not limited to these. Let's consider
another example to showcase the expansive potential of Swift Macro.

In real-world scenarios, we often start from simple structs:

```swift
struct User {

  var name: String

  var avatar: URL

}
```

But as the size of the repository grows, the struct may grow at the same
speed:

```swift
struct User {

  var name: String

  var avatar: URL

  var avatarsInDifferentScales: [Int : URL]

  var userID: String

  var socialMedias: [String]

  var brief: String

  // ...

}
```

Since each property in the `struct` I showed above engaged a heap
allocation to store the data, the cost of copying this struct is increased
at the same time -- how many heap allocations bring how many retain
operations. Since retaining shall be guaranteed to be atomic, this may
cause lagging in user interactions and waste in memory space.

To reduce the cost of copying the struct, we can aggregate the properties
into a class instance which serves as the storage, implementing the
copy-on-write behavior on the original struct when mutating the contents
in the storage:

```swift
struct User {

  // The heap storage type that aggregates the original stored properties
  // in the struct.
  private class Storage {

    var name: String

    // other properties ...

  }

  // The instance of the heap storage.
  private var _storage: Storage

  init(name: String, ...) {
    self._storage = Storage(name: name, ...)
  }

  // Offers copy-on-write behavior.
  private func makeStorageUniqueIfNeeded() {
    if !isKnownUniquelyReferenced(&_storage) {
      _storage = Storage(name: name, ...)
    }
  }

  // A rewritten property in the struct.
  var name: String {
    get { return _storage.name }
    set {
      makeStorageUniqueIfNeeded()
      _storage.name = newValue
    }
  }

  // Other rewritten properties ...

}
```

By adopting this technique for several heavily used structs in a real app
produced by ByteDance, I improved user interaction, increasing the fps
from 48 to 56 and reducing memory usage by 600MB during debugging.

TODO: Before-after comparison for the optimization of the app I mentioned

But, again, this can be cumbersome. It not only involves a lot of
hand-roll code but, worse still, it increases the cost of maintaining the
program. With Swift Macro, we can do this more elegantly.

```swift
@COW
struct User {

  var name: String

  var avatar: URL

  var avatarsInDifferentScales: [Int : URL]

  var userID: String

  var socialMedias: [String]

  var brief: String

  // ...

}
```

Yes. Just as simple as I've shown. By adding an attached macro called
`@COW` to the struct, we have introduced the copy-on-write behavior to
this struct. What this macro did is nothing more than what we have
hand-rolled in the previous code -- adding heap storage to the struct and
transforming the stored properties into computed properties that forward
access to the heap storage. However, the cost of maintenance has not
increased this time.

```swift
@COW
struct User {

  // @COW expansion began
  private class Storage {

    var name: String

    // other properties ...

  }

  private var _$storage: Storage

  private func makeStorageUniqueIfNeeded() {
    if !isKnownUniquelyReferenced(&_$storage) {
      _$storage = Storage(name: name, ...)
    }
  }

  init(name: String, ...) {
    self._storage = Storage(name: name, ...)
  }
  // @COW expansion ended

  // @COW expansion began
  @COWIncluded(storage: _$storage)
  // @COW expansion ended
  var name: String {
    // @COWIncluded expansion began
    get { return _$storage.name }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.name = newValue
    }
    // @COWIncluded expansion ended
  }

}
```

From the macro expansion shown above, it can be observed that attached
Swift macros can extend types with members and rewrite properties by
adding accessors. The extended contents not only bring new behaviors to
the type but also share the "namespace" of the extended point. It is also
worth noting that adding accessors to a stored property also changed its
semantics from a stored property into a computed property.

## Conclusion

By learning from the historical context of existing code reuse methods in
Swift to the properties of the new blood -- Swift macros, we can conclude
that:

- Swift Macro is yet another form of encapsulation. What you were unable
  to implement before the introduction of Swift Macro remains
  unimplementable.
- Swift Macro generates codes by understanding the programmer's code at
  the compile time. This means that we can also do compile-time checking
  with the programmer's code.
- Unlike existing code reuse features in Swift, Swift Macro does not
  protect its expansion from the existing contents of the applied site by
  default. Yet, it also can change the semantics of the applied site.
  Macro authors shall watch out for potential traps and pitfalls while
  implementing Swift macros.
  - For freestanding Swift macros, they can affect the control flow of the
    applied site as well as share the lexical scope.
  - For attached Swift macros, they can extend members to types as well as
    accessors to properties. The extended contents also share the same
    "namespace" of the extended point. More than that, accessor macros
    could turn a stored property into a computed property by adding either
    the `get`, `set` or whatever accessor.

TODO: Figure: modules/types/functions v.s. macro

These properties offer programmers not only another option for code reuse
but also the ability to encapsulate programming concepts that involve
compile-time checking, control flow manipulations, and adding behaviors to
types without relying on inheritance or other runtime techniques. These
properties have never been implemented in Swift before. Without a doubt,
they are the unique strengths of Swift Macro.

However, what brings Swift Macro advantages also introduces traps and
pitfalls. This is an independent topic that we will discuss in the
following post.
