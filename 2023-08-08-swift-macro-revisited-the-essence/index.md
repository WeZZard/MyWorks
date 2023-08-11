---
title: "Swift Macro: Revisited - The Strengths"
category: Programming
tags: [Swift, Macro]
isPublished: false
---

From relative sessions at WWDC 2023, we've learned that Swift Macro aims
to:

- Eliminate boilerplates
- Make tedious things easy
- Share with other developers in packages

However, these goals are not exclusive to Swift Macro; they are common
targets for most common language features in Swift such as function, type
and module. One could argue that all high-level programming languages
aspire to these ends. There must be something else that Swift Macro excels
at, otherwise, it would be redundant.

So, what is it that Swift Macro does exceptionally well?

The answer to this question is critical. It would inspire us to create
Swift macros that hit the points, tell us the boundaries of behaviors
while creating Swift macros, and ultimately guide us to ship
better-designed Swift macros. This is the essence of Swift Macro.

To have this answer, we must first comprehend the problems that existing
Swift language features like function, type and module have managed to
solve and their limitations. The key to understanding Swift Macro lies in
this exploration.

## An Exploration of Existing Reuse Features

TODO: Function & structured programming could be merged

"Function" is ubiquitos in high-level programming languages. They might
have different names across languages — subroutine, routine, subprogram,
or procedure — however, the essence remains the same: providing reusable
units of execution. This has not been changed since the concept of
function was initially brought to high-level programming languages by
FORTRAN with the name "subroutine".

TODO: An example of the FORTRAN subroutine.

As programming evolved, people then have found that programs could be
better understood if:

- Variables are only accessible within the block of a control structure
  like the `IF` statement or loop.
- Control structures could be more expressive like using
  `IF-THEN-ELSE-END` instead of a simple `IF` statement.
- The `GOTO` statement could be eliminated by more advanced control
  structures.
- The "function" could be defined within other "functions".

All these points above comprised the concept of structured programming.
Structured programming was a broad movement in computer science. As a
pioneer in this movement, ALGOL 60 adopted these principles at very early
stage. Swift functions also take these principles as its fundamental
pillars.

TODO: An example of ALGOL 60's structured programming

The adoption of structured programming made programs more comprehensible,
paving the way for more developers to join the field. As software
solutions aimed to address increasingly complex real-world problems,
managing code became a challenge since the only available tool for
organizing code was functions, which meant code could only be reused at a
very granular level or the entire file adn directory.

Simula, which encoded designing for simulating real-world processes in its
name, introduced the concept of object-oriented programming, allowing
developers to create types with variables and functions as members. These
members were accessed via dot notations and were scoped within the type.
Additionally, one type could inherit from another, further enhancing code
reusability. Swift types uphold these practices.

TODO: Figure: dot notation and type inheritance

However, there are still challenges lied before programmers. How to reuse
code between projects? Copy and paste? How to accelerate compilation by
avoiding the commonly reused code? Buy more powerful machines? Modula-2
introduced the concept of modules to address these issues, keeping
developers away from tedious pushes on keyboards and money talks.

Modules brought by Modula-2 enabled encapsulation of code on a granular
level greater than types. More than that, this feature also brought
separate compilation and segregation between interfaces and
implementations which bring faster build speed and better software design.
These advantages now emerged in Swift modules.

TODO: Figure: module-level code reuse and lexical scope

## What Swift Macros Do Exceptionally Well?

By exploring the development history of code reusing, we can find that
people tend to create concepts that aggregate the smaller ones with a
protective mechanism. Let me give you examples:

- Functions aggregate execution flows and variables and protect them
  with control structures and lexical scopes;
- Types aggregate variables and functions and protect them with
  instance name or type name;
- Modules aggregate variables, types and functions and protect them
  with the module's namespaces;

TODO: Figure: protection hierarchy of modules/types/functions

These help us keep the program easy to understand as the code size
increases. But we can still find that there are many critical programming
concepts cannot be encapsulated with them. Let me show you some typical
examples.

### Compile-Time Checked Literals

Since design softwares like Figma or Sketch represent the RGB color with 6
hexadecimal digits, the developers would often have the following
extension in Swift such that they can directly copy and paste the RGB
values displayed in the design software and use them in SwiftUI:

```swift
import SwiftUI

// Color extension
extension Color {

  public init(_ hex: UInt)

}

// Use example
Color(0xFFEEAA)
```

But how do I know the pasted value represents a valid RGB color? Since we
are copying and pasting, the digits themselves could be shorter than what
it was in the original place.

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

In real-world programming, we always want to get rid of the following
code that explicitly unwraps an optional value with an exclamation mark:

```swift
func foo(_ bar: Int?) {
  print(bar!)
}
```

Instead, we prefer the code like below:

```swift
func foo(_ bar: Int?) {
  guard let bar else {
    return
  }
  print(bar)
}
```

But it's tedious. You may have to `guard let ... else` many times in one
single function's body if there are multiple optional parameters. This
heavy form of safety guarantee waters things down. We don't have to write
a lot of code to do a trivial thing.

However, since a function protects its internal execution flow for the
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

But Swift Macro does not have this constraint. We can have a macro called
`#unwrapped` which is used as the code shown below:

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
`print` function is the variable declared by the `guard let bar` statement
which is also brought by the expansion of `#unwrapped` macro. This shows
that the expansions of Swift macros share the lexical scope of the applied
site.

From what we've learned, we can have a conclusion that with Swift macro we
can encapsulate programming concepts that
**involve control flow manipulations** and **lexical scope sharing**.

### Extending Type's Behavior

The capabilities of Swift Macro are not limited to these. Let's consider
another example to showcase the expansive potential of Swift Macro.

In real-world programming stories, we always start from simple structs
like the below:

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

Since each property in the `struct` I showed above engaged a heap storage
allocation to store the data, the cost of copying this struct is increased
at the same time -- the count of heap storage here means the count of
object retain operations and retaining shall be guaranteed to be atomic.
This may cause lagging in user interactions and waste in memory space. By
adopting this technique to several heavily used `struct`s of a real app
produced by ByteDance, I've improved the user interaction by increasing
the fps from 48fps to 56fps and decreasing 600MB memory usage.

TODO: Before-after comparison for the optimization of the app I mentioned

To reduce the cost of copying the struct, we can aggregate the properties
to a class instance which is supposed to be the storage, then implement
the copy-on-write behavior on the original struct when we are mutating the
contents in the storage:

```swift
struct User {

  private class Storage {

    var name: String

    // other properties ...

  }

  private var _storage: Storage

  init(name: String, ...) {
    self._storage = Storage(name: name, ...)
  }

  private func makeStorageUniqueIfNeeded() {
    if !isKnownUniquelyReferenced(&_storage) {
      _storage = Storage(name: name, ...)
    }
  }

  var name: String {
    get { return _storage.name }
    set {
      makeStorageUniqueIfNeeded()
      _storage.name = newValue
    }
  }

}
```

But, again, this is tedious. We not only have to write a lot of code to
reduce the cost of copying that struct but, worse still, it increased the
cost of maintaining the program. With Swift Macro, we can do this more
elegantly.

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

Yes. Just as simple as I've shown. By adding an `@COW` attribute to the
struct, we have introduced the copy-on-write behavior to this struct. What
this macro did is nothing more than what we have hand-wired in the
previous code. However, the cost of maintaining the program has not
increased this time.

```swift
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

## Recap

With the examples above, we can learn that:

- Swift Macro is a way of encapsulation. What you are unable to implement
  before Swift Macro was introduced remains the same.
- Swift Macro generates codes by understanding the programmer's code at
  the compile time. This means that we can also do compile-time checking
  with the programmer's code.
- Freestanding Swift macros in a function can affect the control flow of
  the applied site and implicitly share the lexical scope.
- Attached Swift macros can extend members to types and extend accessors
  to properties. The extended contents also share the same "namespace" of
  the extended point.

These properties not only offer the programmers yet another option for
code reuse but also enable them to encapsulate programming concepts that
may involve compile-time checking, control flow manipulations and adding
behaviors to types without inheritance or other runtime techniques. This
has never been implemented in Swift before. Yet, they are the essence of
Swift Macro.
